import axios, { AxiosInstance } from "axios";
import { WebsocketAuth } from "./types";
import { detectSchemeFromHostname, ParseJwt } from "./utils";




function getClient(): AxiosInstance {
    const token = localStorage.getItem("token");
    // TODO: change hardcoded hostname
    const hostname = "http://localhost:5000" //localStorage.getItem("hostname");
    if (token == "") { // || hostname == "") {
        // ask the user to login once again
        window.location.replace("/login");
    }
    let scheme = detectSchemeFromHostname(hostname)
    return axios.create({
        baseURL: `${hostname}/api/v1`,
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });
}

// GRT /api/v1/tasks/create
export function CreateNewTask(name: string, schedule: string, description: string, success: Function, error: Function) {
    if (name == "" || schedule == "") {
        error("Make sure that all the fields are filled.")
        return
    }
    getClient().post("/tasks/create", {
        "task": {
            "name": name,
            "schedule": schedule,
            "description": description,
        },
    }
    ).then(response => {
        success(response.data);
    }).catch(e => { error(e) });
}


// GRT /api/v1/task/:task_id/update
export function UpdateTask(task_id: string, name: string, schedule: string, description: string, success: Function, error: Function) {
    if (name == "" || schedule == "" || task_id == "") {
        error("Make sure that all the fields are filled.")
        return
    }
    getClient().post(`/task/${task_id}/update`, {
        "task": {
            "name": name,
            "schedule": schedule,
            "description": description,
        },
    }
    ).then(response => {
        success(response.data);
    }).catch(e => { error(e) });
}


// GET /api/v1/task/:task_id/completed
export function GetTaskCompletionStatus(task_id: string, success: Function, error: Function) {
    getClient().get(`/task/${task_id}/completed`)
    .then(response => {
        success(response.data);
    }).catch(e => { error(e) });
}

// POST /api/v1/task/:task_id/completed
export function SetTaskCompleted(task_id: string, success: Function, error: Function) {
    getClient().post(`/task/${task_id}/completed`)
    .then(response => {
        success(response.data);
    }).catch(e => { error(e) });
}


// POST /api/v1/task/:task_id/reset
export function ResetTaskCompletion(task_id: string, success: Function, error: Function) {
    getClient().post(`/task/${task_id}/reset`)
    .then(response => {
        success(response.data);
    }).catch(e => { error(e) });
}

export function GetTasksList(success: Function, error: Function) {
    let data = [
        {
            "task": {
                "id": "13a2f3f4-a263-4fae-b95a-51c01e08831a",
                "name": "Test task",
                "schedule": "18:00",
                "description": "This is a test task",
            }
        },
        {
            "task": {
                "id": "da6e335f-a340-4869-ad2e-15c6d19e0c82",
                "name": "Test task",
                "schedule": "18:00",
                "description": "Swim",
            }
        },
        {
            "task": {
                "id": "4766f30a-defa-44e2-ad43-6c8453b0490e",
                "name": "Test task",
                "schedule": "18:00",
                "description": "Run",
            }
        },
        {
            "task": {
                "id": "1b03e6be-2a1c-4c2f-9dd1-834272ea37b5",
                "name": "Test task",
                "schedule": "18:00",
                "description": "Sleep",
            }
        },
        {
            "task": {
                "id": "49257842-7417-4503-8658-6c6412cfa974",
                "name": "Test task",
                "schedule": "18:00",
                "description": "Anime",
            }
        }
    ]

    success(data);

    // TODO: use real values
    /*
    getClient().get(`/tasks/list/`).then(response => {
        success(response.data);
    }).catch(e => { error(e)});*/
}

export function GetTaskMetadata(task_id: string, success: Function, error: Function) {
    getClient().get(`/task/${task_id}/`).then(response => {
        success(response.data);
    }).catch(e => { error(e)});
}

export function DeleteTask(task_id: string, success: Function, error: Function) {
    getClient().get(`/task/${task_id}/delete`).then(response => {
        success(response.data);
    }).catch(e => { error(e)});
}




export async function GetWebsocketId(): Promise<WebsocketAuth> {
    return 
    const res = await getClient().get("/");
    let id = (<{id: string}>res.data).id;
    let token = localStorage.getItem("token");
    let userId = ParseJwt(token).id
    let hostname = localStorage.getItem("hostname");
    return {"id": id, "userId": userId, "hostname": hostname};
}