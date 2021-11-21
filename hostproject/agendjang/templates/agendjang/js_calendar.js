// template dynamic js, why not,

// wrapper for ajax put
function put(url_, data_, callback_) {
    $.ajax({
        url: url_,  // leave trailing /
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data_),
        success: callback_,
    });
}

// $.post ajax is somewhat more buggy... even with json flag
function post(url_, data_, callback_) {
    $.ajax({
        url: url_,  // leave trailing /
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data_),
        success: callback_,
    });
}

function django_date(date_) {
    /* Wrapper for moment.js(used by fullcal),
     here the date have always the same format even if hours missing
    => 2017-11-28T13:00:00
    'T' is escaped because of a bug https://github.com/moment/moment/issues/4081
    */
    return date_.format('YYYY-MM-DD[T]HH:mm:ss');
}

function f_post_daterange(start, end, task_id, callback_) {
    let post_daterange = {
            // le fait d'avoir une variable fait que c'est plus de json de base
            start_date: django_date(start),
            end_date: django_date(end),
            task: task_id,
        };
    post("{% url 'api:dateranges-list'%}", post_daterange, callback_)
}

function put_daterange(event) {
    /*Modyfy daterange according to event data*/
    let daterange = {
        start_date: django_date(event['start']),
        end_date: django_date(event['end']),
        task: event['task_id'],
    };

    // jquery .put doesnt exist.. put wrapper
    put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
        function(data) {}
    );
}

function postTaskFormData(datee) {
    let formData = new FormData(document.querySelector('form'))

    let xhr = new XMLHttpRequest();
    xhr.responseType = 'json';  // allow to convert formData to json automatically
    xhr.onreadystatechange = function() {  // callback
    if (xhr.readyState === XMLHttpRequest.DONE) {
        let task_id = xhr.response.id
            // call function defined in parent window
            window.parent.f_post_daterange(datee, datee, task_id, function(response) {
                location.reload()  // refresh page
            })
        }
    }
    xhr.open("POST", "{% url 'api:tasks-list' %}");
    xhr.send(formData)
}

$(document).ready(function() {  // called when page completly loaded

    // helper: view-source:https://fullcalendar.io/js/fullcalendar-3.7.0/demos/agenda-views.html

    //load the accordiion UI for the accord class
    $(".accord").accordion({ collapsible: true, active: false }); // keep open multiple sections

    $('#calendar').fullCalendar({
        // put your options and callbacks here
        editable: true,  // event on the calendar can be modified
        droppable: true, // allow external event drop
        forceEventDuration: true, // if not all day and no end date, create default end date
        slotLabelFormat: 'H(:mm)',  //24h date format
        firstDay: 1, // start monday

        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay,listWeek'
        },
        views: { // like general option, but only apply to specific views
            week: {
                columnFormat: 'ddd D/M', //overides also for month view
            },
        },

        events: "{% url 'api:events-list'%}", // fullcalendar handles the call format

        // when we clic a day..
        dayClick: function(datee) {  // on rajoute comme arg ce que l'on veut recup ds la callback, rien sinon

            $('#task_dialog').data('ajaxCall', function (){postTaskFormData(datee)}).load("create_task", function() { // relative url, resolver useless
                $('#task_dialog').dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
                // modify input button to send AJAX request
                $('#task_input')
                    .attr('onclick', '$(\'#task_dialog\').data(\'ajaxCall\')()')
                    .attr('type', 'button')
                    .val('SubmitAjax')  // rename field
            });
        },


        // quand on clique sur un event..
        eventClick: function(event) { // on aussi avoir la position de la souris, la vue etc..
            // c'est propre mais c pas de l'ajax, faut reload la page a chaque post..
            // en revanche, ca va bien ac les event init via django template..
            $('#task_dialog').load("update_task/"+event['task_id']) // relative url, resolver useless
                .dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
        },

        // when dragndrop finished and datetime changed (internal event dragndrop)
        eventDrop: function(event, delta, revertFunc) {
            put_daterange(event)
        },

        // when timestamp resize is finished and time changed
        eventResize: function(event, delta, revertFunc) {
            put_daterange(event)
        },

        drop: function(date) {
            // for low level data callback of external drop, not usefull. called before event receive
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(event, view) {

            // fixme shedtask broken because not initialized with task_id
            // post a new daterange, but if form is cancelled it's keeped in db
            f_post_daterange(event.start, event.end, event.task_id, function(response) {
                event.id = response['id']; // id of event is id of daterange
                $('#calendar').fullCalendar('updateEvent', event);

                if (event.is_schedtask)  {  // for the first creation of schedtask
                    // get the DOM, modify it by inserting the new daterange key (
                    $(event.dom[0]).load(event.dom[1], function() {  // no need async to popup dialog but to modify the DOM before
                        $('#id_many_dateranges').empty().append("<option selected='selected' value="
                         + event.many_dateranges + ">  La bonne date </option>");  // modify form to auto add the daterange
                        $(event.dom[0]).dialog({width: 'auto'});  // load pop up
                    });
                }
            });
        },

    })

});
