
import { login, register, isLoggedIn } from './auth'
import { parseUserId } from './utils'
import { AddFriend, CreateNewTask, GetFriendStatus, GetMaxTaskStreakStatus, GetSelfInfo, GetTaskCompletionStatus, GetTasksList, GetTaskStreakStatus, ResetTaskCompletion, SetTaskCompleted, Unfriend, UpdateTask } from "./api"
import { ListenEventChanges } from './ws'
import { AxiosError } from 'axios';


function registerHtmlCallback() {
    let registerButton = (<HTMLButtonElement>document.getElementById('submitButton'));
    registerButton.classList.add('is-loading');
    let name = (<HTMLInputElement>document.getElementById('full_name')).value
    let username = (<HTMLInputElement>document.getElementById('userId')).value
    let password = (<HTMLInputElement>document.getElementById('password')).value
    let confirmedPassword = (<HTMLInputElement>document.getElementById('confirm_password')).value
    if (password != confirmedPassword) {
        alert('Passwords do not match')
        return
    }

    register(username, password, name, function() {
        window.location.replace("/login");
    }, 
    function() {
        alert('Registration failed')
        registerButton.classList.remove('is-loading');
    })   
}


function loginHtmlCallback() {
    let userId = (<HTMLInputElement>document.getElementById('userId')).value
    let password = (<HTMLInputElement>document.getElementById('password')).value
    login(userId, password, function() {
        const urlParams = new URLSearchParams(window.location.search);
        const next: string = urlParams.get('next');
        let nextUrl = "/"
        if (next != null && next != "") {
            nextUrl = decodeURI(next)
        }
        window.location.replace(nextUrl);
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

function refreshFriendStatus (addFriendButton: HTMLElement, friends: boolean) {
    let label = document.getElementById("streak__button-new_task_create-label")
    if (!friends) {
        addFriendButton.classList.add('is-primary')
        addFriendButton.classList.remove('is-error')
        label.textContent = "Add Friend"
    } else {
        addFriendButton.classList.remove('is-primary')
        addFriendButton.classList.add('is-error')
        label.textContent = "Remove Friend"
    }
    addFriendButton.classList.remove('is-loading')

}

function onUserPageLoadCallback() {
    let addFriendButton = document.getElementById('streak__button-new_task_create')
    GetFriendStatus(addFriendButton.dataset.userId, function(resp: { friends: boolean; }) {
        refreshFriendStatus(addFriendButton, resp.friends)
        addFriendButton.onclick = function() {
            addFriendButton.classList.add('is-loading')
            if (addFriendButton.classList.contains('is-primary')) {
                AddFriend(addFriendButton.dataset.userId, function() {
                    refreshFriendStatus(addFriendButton, true)
                }, function() {
                    alert("Couldn't add friend")
                    addFriendButton.classList.remove('is-loading')
                })
            } else {
                Unfriend(addFriendButton.dataset.userId, function() {
                    refreshFriendStatus(addFriendButton, false)
                }, function(err: Error) {
                    console.log(err)
                    alert("Couldn't add friend")
                    addFriendButton.classList.remove('is-loading')
                })
            }
        }

    }, function (err: AxiosError) {
        if (err.response.status == 403) {
            console.log("Disabling button to prevent being friends with self, meh")
            addFriendButton.classList.remove("is-loading")
            addFriendButton.classList.add("is-primary")
            
            addFriendButton.textContent = "Dashboard"
            addFriendButton.addEventListener('click', function() {
                window.location.replace("/")
            })
            return
        }
        alert("Failed fetching friend status")
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


function taskDetailsCallback() {
    let taskEditButton = document.getElementById('streak__button-new_task_create')
    let currentStreak = document.getElementById('streak__title-current_streak')
    let current2Streak = document.getElementById('streak__title-current_streak_current')
    let monthlyStreak = document.getElementById('streak__title-current_streak_monthly')
    let yearlyStreak = document.getElementById('streak__title-current_streak_yearly')
    let alltimeStreak = document.getElementById('streak__title-current_streak_alltime')
    let currentStreakDescription = document.getElementById('streak__title-current_streak-description')
    GetTaskStreakStatus(taskEditButton.dataset.taskId, function(resp: { streak: number; }) {
        currentStreak.textContent = `${resp.streak}`
        current2Streak.textContent = `${resp.streak}`
        if (resp.streak == 1) {
            currentStreakDescription.textContent = "day on streak"
        } else {
            currentStreakDescription.textContent = "days on streak"
        }
    }, function () {
        console.log("Failed to get streak status")
        currentStreak.textContent = `${0}`
        currentStreakDescription.textContent = "days on streak"
    })
    GetMaxTaskStreakStatus(taskEditButton.dataset.taskId, function(resp: { month: number; year: number; all_time: number; }) {
        monthlyStreak.textContent = `${resp.month}`
        yearlyStreak.textContent = `${resp.year}`
        alltimeStreak.textContent = `${resp.all_time}`
    }, function () {
        console.log("Failed to get streak status")
        monthlyStreak.textContent = `${0}`
        yearlyStreak.textContent = `${0}`
        alltimeStreak.textContent = `${0}`
    })
}


function onDefaultPageUpdateStatus() {
    let date = new Date();
    let hrs = date.getHours();
    let greet = "Good day!";
    if (hrs < 12)
        greet = 'Good Morning';
    else if (hrs >= 12 && hrs <= 17)
        greet = 'Good Afternoon';
    else if (hrs >= 17 && hrs <= 24)
        greet = 'Good Evening';
    
    let status =  document.getElementById('streak__h2-status')
    GetSelfInfo(function(resp: { name: string; }) {
        status.innerText = `${greet}, ${resp.name}.`
    }, function() {
        status.innerText = `${greet}.`
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
        case /\/register.*/.test(window.location.pathname):
            registerRegisterButtonCallback()
            break; 
        case  /\/login.*/.test(window.location.pathname):
            registerLoginButtonCallback()
            break;
        case  /\/task\/.*/.test(window.location.pathname):
            onDefaultPageLoadCallback()
            taskDetailsCallback()
            navBarSetup()
            break;
        case /\/\@.*/.test(window.location.pathname):
            navBarSetup()
            onUserPageLoadCallback();
            
            break

        case /\//.test(window.location.pathname):
            onDefaultPageLoadCallback()
            navBarSetup()
            onDefaultPageUpdateStatus()
            ListenEventChanges()

            break

        default:
            onDefaultPageLoadCallback()
            navBarSetup()
            break;
    }
}
