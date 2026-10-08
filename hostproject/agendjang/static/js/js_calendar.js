// API urls are resolved by django and passed as data-* attributes on this script's tag;
// document.currentScript is only set while the script is first executing, so read them now
const urls = document.currentScript.dataset;

function getCookie(name) {
    /*from django docs. parse cookie*/
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// JSON request to the REST API; leave trailing / on url. Rejects when the backend refuses the change
function apiRequest(method, url, data) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    }).then(response => {
        if (!response.ok) throw new Error(`${method} ${url} failed with status ${response.status}`);
    });
}

function toDaterange(event, end = event.end) {
    return {
        start_date: event.start.toISOString(),
        end_date: end.toISOString(),
        task: event.extendedProps.taskId,
    };
}

// the calendar already shows the change: persist it, revert it if the backend refuses it, then
// refetch the events either way, since part of their data (e.g. color) is computed by the backend
function persistChange(request, revert) {
    request
        .catch(error => {
            console.error(error);
            revert();
        })
        .finally(() => calendar.refetchEvents());
}

// reloads the tags sidebar, keeping its accordions open state
function reloadTagList() {
    const tagList = document.getElementById('tag_list');
    const openTagIds = [...tagList.querySelectorAll('details[open]')].map(details => details.dataset.tagId);

    fetch(urls.tagListUrl)
        .then(response => response.text())
        .then(html => {
            tagList.innerHTML = html;
            openTagIds.forEach(tagId => tagList.querySelector(`details[data-tag-id="${tagId}"]`).open = true);
        });
}

// loads dialog content from another url, then shows the dialog;
// resolves with the dialog's content element once it's filled
function loadDialog(domId, relUrl) {
    const dialog = document.querySelector(domId);
    const content = dialog.querySelector('.dialog-content');
    dialog.showModal();
    return fetch(relUrl)
        .then(response => response.text())
        .then(html => {
            content.innerHTML = html;
            return content;
        });
}

// dialog forms are posted to their classic django form view without leaving the page: the view
// redirects on success (not followed, the redirect target is the whole calendar page),
// otherwise it answers with the form re-rendered with its errors
document.addEventListener('submit', function(submitEvent) {
    submitEvent.preventDefault();
    const form = submitEvent.target;

    fetch(form.action, { method: 'POST', body: new FormData(form), redirect: 'manual' })
        .then(response => {
            if (response.type === 'opaqueredirect') {
                form.closest('dialog').close();
                calendar.refetchEvents();
                reloadTagList();
            } else {
                // only the form is replaced, so buttons added next to it (e.g. unlink) are kept
                return response.text().then(html => form.outerHTML = html);
            }
        });
});

let calendar;

document.addEventListener('DOMContentLoaded', function() {  // called when page is completely loaded

    const calendarEl = document.getElementById('calendar');
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: true,  // event on the calendar can be modified
        droppable: true, // allow external event drop
        forceEventDuration: true, // if not all day and no end date, create default end date
        slotLabelFormat: { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' },  // 24h time format
        eventTimeFormat: { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' },
        firstDay: 1, // start monday

        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        },
        views: { // like general option, but only apply to specific views
            timeGridWeek: {
                dayHeaderFormat: { weekday: 'short', month: 'numeric', day: 'numeric' },
            },
        },

        events: urls.eventsUrl, // fullcalendar handles the call format

        dateClick: function(info) {
            // a task created by clicking a day spans the full day (24h = allDay, per the API's own convention)
            const end = new Date(info.date);
            end.setDate(end.getDate() + 1);

            const dateRange = new URLSearchParams({ start_date: info.date.toISOString(), end_date: end.toISOString() });
            loadDialog('#task_dialog', 'create_task?' + dateRange);
        },

        eventClick: function(info) {
            const event = info.event;

            loadDialog('#task_dialog', 'update_task/'+event.extendedProps.taskId)
                .then(content => {
                    // add unlink button to dialog
                    const unlinkBtn = document.createElement('input');
                    unlinkBtn.type = 'button';
                    unlinkBtn.value = 'Unlink the date';
                    unlinkBtn.onclick = function () {
                        content.closest('dialog').close();
                        event.remove();
                        // nothing to revert by hand: the refetch brings the event back
                        persistChange(apiRequest('DELETE', urls.daterangesUrl+event.id+'/'), () => {});
                    };
                    content.appendChild(unlinkBtn);
                });
        },

        // when dragndrop finished and datetime changed (internal event dragndrop)
        eventDrop: function(info) {
            const event = info.event;
            let end = event.end;
            if (event.allDay) {  // in our data model, an event is considered all day if it last 24hours
                // in fullcalendar, an allDay event just takes into account "start" and "allDay=true"
                end = new Date(event.start);
                end.setDate(end.getDate() + 1);
            }
            persistChange(apiRequest('PUT', urls.daterangesUrl+event.id+'/', toDaterange(event, end)), info.revert);
        },

        // when timestamp resize is finished and time changed
        eventResize: function(info) {
            const event = info.event;
            persistChange(apiRequest('PUT', urls.daterangesUrl+event.id+'/', toDaterange(event)), info.revert);
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(info) {
            // FullCalendar keeps its own client-side copy of the dropped event, outside the events source,
            // so a refetch wouldn't replace it: it's removed on success too, in favor of the backend's version
            persistChange(
                apiRequest('POST', urls.daterangesUrl, toDaterange(info.event)).then(() => info.event.remove()),
                info.revert,
            );
        },

    });
    calendar.render();

    // makes tasks in the tag sidebar draggable onto the calendar
    new FullCalendar.Draggable(document.getElementById('tags'), {
        itemSelector: '.task_div',
        eventData: function(eventEl) {
            return {
                title: eventEl.dataset.title,
                extendedProps: { taskId: eventEl.dataset.taskId },
            };
        }
    });

});
