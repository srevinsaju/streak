
import { login, register, isLoggedIn } from './auth'
import { parseUserId } from './utils'
import { CreateNewTask, GetTaskCompletionStatus, GetTasksList, ResetTaskCompletion, SetTaskCompleted, UpdateTask } from "./api"
import { ListenEventChanges } from './ws'


function registerHtmlCallback() {
    let username = (<HTMLInputElement>document.getElementById('userId')).value
    let password = (<HTMLInputElement>document.getElementById('password')).value
    let confirmedPassword = (<HTMLInputElement>document.getElementById('confirm_password')).value
    if (password != confirmedPassword) {
        alert('Passwords do not match')
        return
    }

    register(username, password, function() {
        window.location.replace("/login");
    }, 
    function() {
        alert('Registration failed')
    })   
}


function loginHtmlCallback() {
    let userId = (<HTMLInputElement>document.getElementById('userId')).value
    let password = (<HTMLInputElement>document.getElementById('password')).value
    let parsed = parseUserId(userId)
    login(parsed.username, password, function() {
        const urlParams = new URLSearchParams(window.location.search);
        const next = urlParams.get('next');
        let nextUrl = "/"
        if (next != null && next != "") {
            nextUrl = decodeURI(next)
        }
        window.location.replace(next);
    }, function() {

    alert('Login failed')

    })   
}

function registerRegisterButtonCallback() {
    (<HTMLButtonElement>document.getElementById('submitButton')).onclick = registerHtmlCallback
}

function registerLoginButtonCallback() {
    (<HTMLButtonElement>document.getElementById('submitButton')).onclick = loginHtmlCallback
}


function tasksUpdateCompleteStatus() {
    let tasks = document.querySelectorAll('.streak__card-tasks_card')
    tasks.forEach(function(task: HTMLElement) {
        GetTaskCompletionStatus(task.dataset.taskId, function(data: { completed: boolean }) {
            task.classList.remove('is-loading');
            if (data.completed) {
                task.classList.add('is-primary')
            }
            task.addEventListener('click', function (data) {
                task.classList.add('is-loading');
                if (task.classList.contains('is-primary')) {
                    ResetTaskCompletion(task.dataset.taskId, function() {
                        task.classList.remove('is-loading');
                        task.classList.toggle('is-primary')
                    }, function(err: Error) {
                        alert(`Failed to toggle task list ${err}`)
                    })

                } else {
                    SetTaskCompleted(task.dataset.taskId, function() {
                        task.classList.remove('is-loading');
                        task.classList.toggle('is-primary')
                    }, function(err: Error) {
                        alert(`Failed to toggle task list ${err}`)
                    })
                }
                
            })
        }, function(err: Error) {
            console.log(`Failed to get status for task ${err}`)
            task.classList.remove('is-loading');
            task.classList.add('is-error')
        })
        
    })

}

function onDefaultPageLoadCallback() {

    let newTaskCreateButton = document.getElementById('streak__button-new_task_create');
    let newTaskModalCreateButton = document.getElementById('streak__modal-new_task_create-create');
    let newTaskCloseButton = document.querySelectorAll('.streak__modal-new_task_create-close')

    let newTaskModal = document.getElementById('streak__modal-new_task_create')
    newTaskCreateButton.addEventListener('click', function () {
        newTaskModal.classList.add('is-active');
    })


    newTaskCloseButton.forEach(function(elem: HTMLElement) {
        elem.addEventListener('click', function () {
            newTaskModal.classList.remove('is-active');
        })
    })


    let newTaskModalMetaTitle = <HTMLInputElement>document.getElementById("streak__modal-new_task_create-title");
    // move schedule to cron, because streaks can be 
    let newTaskModalMetaSchedule = <HTMLInputElement>document.getElementById("streak__modal-new_task_create-schedule");
    let newTaskModalMetaDescription = <HTMLInputElement>document.getElementById("streak__modal-new_task_create-description");
    newTaskModalCreateButton.addEventListener('click', function () {
        newTaskModalCreateButton.classList.add('is-loading');
        
        if (/\/task\/.*/.test(window.location.pathname)) {
            // we need to update the task details
            UpdateTask(
                newTaskCreateButton.dataset.taskId ,
                newTaskModalMetaTitle.value,
                newTaskModalMetaSchedule.value,
                newTaskModalMetaDescription.value,
                function() {
                    
                    newTaskModalCreateButton.classList.remove('is-loading');
                    newTaskModal.classList.remove('is-active');
                    // move to something like an inline html alert
                    location.reload();
                },
                function(e: Error) {
                    newTaskModalCreateButton.classList.remove('is-loading');
                    alert(`Something went wrong! I couldn't create a task for you 😔. ${e}`)
                },
            )

        } else {
            // the user hit the create task button 
            CreateNewTask(
                newTaskModalMetaTitle.value,
                newTaskModalMetaSchedule.value,
                newTaskModalMetaDescription.value,
                function() {
                    
                    newTaskModalCreateButton.classList.remove('is-loading');
                    newTaskModal.classList.remove('is-active');
                    // refresh the page so that the UI is updated
                    location.reload();

                },
                function(e: Error) {
                    newTaskModalCreateButton.classList.remove('is-loading');
                    alert(`Something went wrong! I couldn't create a task for you 😔. ${e}`)
                },
            )

        }
        
    })

    tasksUpdateCompleteStatus()

}


function navBarSetup() {
    let navBar =  <HTMLButtonElement>document.getElementsByClassName('navbar-burger').item(0)
    navBar.onclick = function() {
        navBar.classList.toggle('is-active')
        document.getElementsByClassName('navbar-menu').item(0).classList.toggle('is-active')
    }   
}


export function registerAllCallbacks() {
    switch (true) {
        case /\/register\//.test(window.location.pathname):
            registerRegisterButtonCallback()
            break; 
        case  /\/login\//.test(window.location.pathname):
            registerLoginButtonCallback()
            break;
        case  /\/task\/.*/.test(window.location.pathname):
            onDefaultPageLoadCallback()
            navBarSetup()
            break;
        case /\//.test(window.location.pathname):
            onDefaultPageLoadCallback()
            navBarSetup()
            ListenEventChanges()

            break

        default:
            onDefaultPageLoadCallback()
            navBarSetup()
            break;
    }
}
