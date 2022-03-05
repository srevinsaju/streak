import { detectSchemeFromHostname } from "./utils";

const axios = require('axios').default;


export function isLoggedIn(): boolean {
    let lKeys = ["token", "username", "hostname"] 
    for (const key in lKeys) {
        if (localStorage.getItem(lKeys[key]) === null) {
            return false;
        }
        // TODO, what if the person's name is null?
        if (localStorage.getItem(lKeys[key]) === "null") {
            return false;
        }
    }
    return true;
}



export function login(
    username: string, 
    password: string,
    success: Function, 
    error: Function)
{
    console.log(`Sending login request to`)
    axios.post(`/api/v1/login`, 
    {
        "username": username, 
        "password": password
    }).then((res: { data: { token: string; }; }) => {
        console.log(`Login successful`)
        success()
    }).catch((err: any) => {
        console.log(`Failed to send login request: ${err}`);
        error(err)
    })
}

export function register(
    username: string, 
    password: string, 
    success: Function, 
    error: Function)
{
    axios.post(`/api/v1/register`, 
    {
        "username": username, 
        "password": password,
    }).then((res: { data: { token: string; }; }) => {
        success()
    }).catch((err: any) => {
        console.log(`Failed to send register request: ${err}`);
        error(err)
    })
}