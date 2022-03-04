
import { login, register, isLoggedIn } from './auth'
import { parseUserId } from './utils'
import { CreateNewTask, GetTasksList, UpdateTask } from "./api"
import { ListenEventChanges } from './ws'


function registerHtmlCallback() {
    let userId = (<HTMLInputElement>document.getElementById('userId')).value
    let password = (<HTMLInputElement>document.getElementById('password')).value
    let confirmedPassword = (<HTMLInputElement>document.getElementById('confirm_password')).value
    if (password != confirmedPassword) {
        alert('Passwords do not match')
        return
    }
    let parsed = parseUserId(userId)

    register(parsed.username, password, parsed.hostname, function() {
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
    login(parsed.username, password, parsed.hostname, function() {
        window.location.replace("/");
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
