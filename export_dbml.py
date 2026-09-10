"""Export the Tortoise model schema as DBML for dbdiagram.io."""

import argparse
import asyncio
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from tortoise import Tortoise

from depot_server.config import TORTOISE_ORM


def dbml_identifier(value: str) -> str:
	"""Quote identifiers that are not simple DBML identifiers."""
	if value.replace("_", "").isalnum() and not value[0].isdigit():
		return value
	return f'"{value.replace(chr(34), chr(34) * 2)}"'


def dbml_type(field: Any) -> str:
	sql_type = getattr(field, "SQL_TYPE", None)
	if sql_type:
		return sql_type.replace(" ", "_").lower()
	return field.__class__.__name__.removesuffix("Field")


def field_settings(field: Any) -> str:
	settings: list[str] = []
	if getattr(field, "pk", False):
		settings.append("pk")
	if getattr(field, "unique", False):
		settings.append("unique")
	if not getattr(field, "null", False) and not getattr(field, "pk", False):
		settings.append("not null")
	return f" [{', '.join(settings)}]" if settings else ""


def model_fields(model: Any) -> Iterable[Any]:
	field_names = sorted(
			model._meta.db_fields,
			key=lambda field_name: field_name != model._meta.pk_attr,
		)
	for field_name in field_names:
		yield model._meta.fields_map[field_name]


def model_pk_column(model: Any) -> str:
	pk_field = model._meta.fields_map[model._meta.pk_attr]
	return getattr(pk_field, "db_column", None) or pk_field.model_field_name


def render_table(model: Any) -> list[str]:
	lines = [f"Table {dbml_identifier(model._meta.db_table)} {{"]
	for field in model_fields(model):
		lines.append(
			f"  {dbml_identifier(field.model_field_name)} "
			f"{dbml_type(field)}{field_settings(field)}"
		)
	lines.append("}")
	return lines


def render_many_to_many(field: Any) -> tuple[list[str], str]:
	through_model = field.through
	through_table = through_model if isinstance(through_model, str) else through_model._meta.db_table
	source_table = field.model._meta.db_table
	target_table = field.related_model._meta.db_table
	source_key = field.backward_key
	target_key = field.forward_key
	source_type = dbml_type(field.model._meta.fields_map[field.model._meta.pk_attr])
	target_type = dbml_type(field.related_model._meta.fields_map[field.related_model._meta.pk_attr])

	lines = [
		f"Table {dbml_identifier(through_table)} {{",
		f"  {dbml_identifier(source_key)} {source_type} [not null]",
		f"  {dbml_identifier(target_key)} {target_type} [not null]",
		"}",
	]
	refs = [
		f"Ref: {dbml_identifier(through_table)}.{dbml_identifier(source_key)} > "
		f"{dbml_identifier(source_table)}.{dbml_identifier(model_pk_column(field.model))}",
		f"Ref: {dbml_identifier(through_table)}.{dbml_identifier(target_key)} > "
		f"{dbml_identifier(target_table)}.{dbml_identifier(model_pk_column(field.related_model))}",
	]
	return lines, "\n".join(refs)


def render_dbml(models: Iterable[Any]) -> str:
	models = sorted(models, key=lambda model: model._meta.db_table)
	lines: list[str] = ["// Generated from depot_server.db2.models", ""]
	references: list[str] = []
	seen_tables: set[str] = set()

	for model in models:
		table = model._meta.db_table
		if table in seen_tables:
			continue
		seen_tables.add(table)
		lines.extend(render_table(model))
		lines.append("")

		for field in model._meta.m2m_fields:
			join_table, join_refs = render_many_to_many(model._meta.fields_map[field])
			if join_table[0] not in lines:
				lines.extend(join_table)
				lines.append("")
			references.extend(join_refs.splitlines())

		for field_name in model._meta.fk_fields:
			field = model._meta.fields_map[field_name]
			related_model = field.related_model
			source_field = field.source_field
			if related_model is not None and source_field is not None:
				references.append(
					f"Ref: {dbml_identifier(table)}.{dbml_identifier(source_field)} > "
					f"{dbml_identifier(related_model._meta.db_table)}."
					f"{dbml_identifier(model_pk_column(related_model))}"
				)

	if references:
		lines.append("\n".join(dict.fromkeys(references)))
	return "\n".join(lines).rstrip() + "\n"


async def export_schema() -> str:
	await Tortoise.init(config=TORTOISE_ORM)
	try:
		models = Tortoise.apps["depot"].values()
		return render_dbml(models)
	finally:
		await Tortoise.close_connections()


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument(
		"-o", "--output", type=Path, help="Write DBML to this file instead of stdout"
	)
	args = parser.parse_args()
	dbml = asyncio.run(export_schema())
	if args.output:
		args.output.write_text(dbml, encoding="utf-8")
	else:
		print(dbml, end="")


if __name__ == "__main__":
	main()

# Print to file using:
#
# PYTHONPATH=src .venv/bin/python export_dbml.py --output depot-schema.dbml

