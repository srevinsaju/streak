import { detectSchemeFromHostname } from "./utils";

const axios = require('axios').default;


export function isLoggedIn(): boolean {
    // TODO: change hardcoded logged in status
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
    name: string,
    success: Function, 
    error: Function)
{
    axios.post(`/api/v1/register`, 
    {
        "username": username, 
        "password": password,
        "name": name,
    }).then((res: { data: { token: string; }; }) => {
        success()
    }).catch((err: any) => {
        console.log(`Failed to send register request: ${err}`);
        error(err)
    })
}