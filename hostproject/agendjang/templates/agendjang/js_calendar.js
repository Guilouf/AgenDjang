// template dynamic js, why not,

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

// wrapper for a JSON PUT request; leave trailing / on url
function put(url, data, callback) {
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
        .then(response => response.ok ? response.json() : null)
        .then(callback);
}

// wrapper for a JSON POST request; leave trailing / on url
function post(url, data, callback) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
        .then(response => response.ok ? response.json() : null)
        .then(callback);
}

function remove(url, callback) {
    // DELETE responses have no body (204 No Content), so there's nothing to parse
    fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
        .then(callback);
}

function djangoDate(date) {
    /* Build a fixed-format datetime string for the Django API from a native Date,
    using local time components, even when the date has no meaningful time part
    (e.g. midnight from a day click)
    => 2017-11-28T13:00:00
    */
    const pad = n => String(n).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` +
        `T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function postDaterange(start, end, taskId, callback) {
    let postDateRange = {
            start_date: djangoDate(start),
            end_date: djangoDate(end),
            task: taskId,
        };
    post("{% url 'agendjang:api:dateranges-list'%}", postDateRange, callback)
}

function putDaterange(event, endOverride) {
    /*Modyfy daterange according to event data. endOverride lets eventDrop force
    a computed end date without mutating the (read-only) FullCalendar event.*/
    let daterange = {
        start_date: djangoDate(event.start),
        end_date: djangoDate(endOverride || event.end),
        task: event.extendedProps.taskId,
    };

    // jquery .put doesnt exist.. put wrapper
    put("{% url 'agendjang:api:dateranges-list'%}"+event.id+'/', daterange,
        function(data) {}
    );
}

function deleteDateRange(dateRangeId) {
    remove("{% url 'agendjang:api:dateranges-list'%}"+dateRangeId+'/',
        function(data) {}
    );
}

function postTaskFormData(date) {
    // scoped to #task_dialog rather than a bare 'form' selector, since a stray
    // form left loaded in another dialog would otherwise be picked up instead
    let formData = new FormData(document.querySelector('#task_dialog form'))

    // a task created by clicking a day spans the full day (24h = allDay, per the API's own convention)
    let end = new Date(date);
    end.setDate(end.getDate() + 1);

    fetch("{% url 'agendjang:api:tasks-list' %}", { method: 'POST', body: formData })
        .then(response => response.ok ? response.json() : null)
        .then(task => {
            if (!task) return;  // validation failed; leave the dialog open instead of silently proceeding
            window.parent.postDaterange(date, end, task.id, function(response) {
                location.reload()  // refresh page
            })
        });
}

document.addEventListener('DOMContentLoaded', function() {  // called when page is completely loaded

    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        editable: true,  // event on the calendar can be modified
        droppable: true, // allow external event drop
        forceEventDuration: true, // if not all day and no end date, create default end date
        slotLabelFormat: { hour: 'numeric', minute: '2-digit', omitZeroMinute: true, meridiem: false },  //24h date format
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

        events: "{% url 'agendjang:api:events-list'%}", // fullcalendar handles the call format

        dateClick: function(info) {
            const dayDate = info.date;
            const dialog = document.querySelector('#task_dialog');

            fetch("create_task") // relative url, resolver useless
                .then(response => response.text())
                .then(html => {
                    dialog.querySelector('.dialog-content').innerHTML = html;
                    // modify input button to send AJAX request instead of a normal form submit
                    const submitBtn = document.querySelector('#task_input');
                    submitBtn.type = 'button';
                    submitBtn.value = 'SubmitAjax';  // rename field
                    submitBtn.onclick = () => postTaskFormData(dayDate);
                });
            dialog.showModal();
        },

        eventClick: function(info) {
            const event = info.event;
            const dialog = document.querySelector('#task_dialog');

            fetch("update_task/"+event.extendedProps.taskId) // relative url, resolver useless
                .then(response => response.text())
                .then(html => {
                    const content = dialog.querySelector('.dialog-content');
                    content.innerHTML = html;
                    // add unlink button to dialog
                    const unlinkBtn = document.createElement('input');
                    unlinkBtn.type = 'button';
                    unlinkBtn.value = 'Unlink the date';
                    unlinkBtn.onclick = function () {
                        deleteDateRange(event.id)  // remove event in db
                        event.remove();  // rm event in calendar
                        dialog.close()  // closes dialog
                    };
                    content.appendChild(unlinkBtn);
                });
            dialog.showModal();
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
            putDaterange(event, end)
        },

        // when timestamp resize is finished and time changed
        eventResize: function(info) {
            putDaterange(info.event)
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(info) {
            const event = info.event;

            // post a new daterange, but if form is cancelled it's keeped in db
            postDaterange(event.start, event.end, event.extendedProps.taskId, function(response) {
                // FullCalendar already auto-inserted its own client-side copy of this event on drop;
                // remove it before refetching, otherwise both it and the server's authoritative
                // version would be shown side by side until the next full page load
                event.remove();
                calendar.refetchEvents();
            });
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
