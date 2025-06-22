import uvicorn
import depot_server.api

if __name__ == "__main__":
    uvicorn.run(depot_server.api.app, port=8000)