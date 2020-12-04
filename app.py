import os
import motor.motor_asyncio
from bson import ObjectId
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.college


async def create_student(request):
    student = await request.json()
    student["_id"] = str(ObjectId())
    new_student = await db["students"].insert_one(student)
    created_student = await db["students"].find_one({"_id": new_student.inserted_id})
    return JSONResponse(status_code=201, content=created_student)


async def list_students(request):
    students = await db["students"].find().to_list(1000)
    return JSONResponse(students)


async def show_student(request):
    id = request.path_params["id"]
    if (student := await db["students"].find_one({"_id": id})) is not None:
        return JSONResponse(student)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


async def update_student(request):
    id = request.path_params["id"]
    student = await request.json()
    update_result = await db["students"].update_one({"_id": id}, {"$set": student})

    if update_result.modified_count == 1:
        if (updated_student := await db["students"].find_one({"_id": id})) is not None:
            return JSONResponse(updated_student)

    if (existing_student := await db["students"].find_one({"_id": id})) is not None:
        return JSONResponse(existing_student)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


async def delete_student(request):
    id = request.path_params["id"]
    delete_result = await db["students"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=204)

    raise HTTPException(status_code=404, detail=f"Student {id} not found")


app = Starlette(
    debug=True,
    routes=[
        Route("/", create_student, methods=["POST"]),
        Route("/", list_students, methods=["GET"]),
        Route("/{id}", show_student, methods=["GET"]),
        Route("/{id}", update_student, methods=["PUT"]),
        Route("/{id}", delete_student, methods=["DELETE"]),
    ],
)
