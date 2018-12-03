// template dynamic js, why not,
$(document).ready(function() {  // called when page completly loaded fixme for external loaded html ??

    // helper: view-source:https://fullcalendar.io/js/fullcalendar-3.7.0/demos/agenda-views.html

    // wrapper for ajax put
    function put(url_, data_, callback_) {
        $.ajax({
            url: url_,  // leave trailing /
            type: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(data_),
            success: callback_,
        });
    };

    // $.post ajax is somewhat more buggy... even with json flag
    function post(url_, data_, callback_) {
        $.ajax({
            url: url_,  // leave trailing /
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data_),
            success: callback_,
        });
    };

    function too_late_color(date_end_, done) {
        now = moment().valueOf();  //js timestamp

        if (now > date_end_ && !done) {
            return "red"
        }
        else if (done) {
            return "green"
        }
    }

    function django_date(date_) {
        /* Wrapper for moment.js(used by fullcal),
         here the date have always the same format even if hours missing
        => 2017-11-28T13:00:00
        'T' is escaped because of a bug https://github.com/moment/moment/issues/4081
        */
        return date_.format('YYYY-MM-DD[T]HH:mm:ss');
    };

    function f_post_daterange(start, end, callback_) {
        post_daterange = {
                // le fait d'avoir une variable fait que c'est plus de json de base
                start_date: django_date(start),
                end_date: django_date(end),
            };
        post("{% url 'api:dateranges-list'%}", post_daterange, callback_)
    }

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


        // init by django tag the existing tasks with timestamp
        events: [
            {% for task in object_list %}
                {% for daterange in task.many_dateranges.all %}
                    {
                        task_id: '{{ task.pk }}',
                        id: '{{ daterange.pk }}',  // diff id even with repeated event
                        title: '{{ task.name }}',
                        // .0 django template list index
                        start: '{{ daterange.start_date | date:'c'  }}', // iso 8601
                        end: '{{ daterange.end_date | date:'c'  }}', // iso 8601
                        // si l'evenement dure 24h, c'est un allday
                        allDay: moment('{{ daterange.end_date | date:'c'  }}').valueOf()
                                - moment('{{ daterange.start_date | date:'c'  }}').valueOf() == 86400000 ? true : false,
                        color: too_late_color(moment('{{ daterange.end_date | date:'c'  }}').valueOf()
                                              , {{task.done|yesno:"true,false"}}  ),// convertit en bool js
                                              // backgroundColor aussi
                    },
                {% endfor %}
            {% endfor %}
        ],




        // when we clic a day..
        dayClick: function(datee) {  // on rajoute comme arg ce que l'on veut recup ds la callback, rien sinon

            f_post_daterange(datee, datee, function(response) {
                $('#task_dialog').load("create_task", function() { // relative url, resolver useless
                    $('#id_many_dateranges').empty().append("<option selected='selected' value="
                     + response['id'] + ">  La bonne date </option>");  // modify form to auto add the daterange
                    $('#task_dialog').dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
                });
            })
        },


        // quand on clique sur un event..
        eventClick: function(event) { // on aussi avoir la position de la souris, la vue etc..
            // c'est propre mais c pas de l'ajax, faut reload la page a chaque post..
            // en revanche, ca va bien ac les event init via django template..
            $('#task_dialog').load("update_task/"+event['task_id']);  // relative url, resolver useless
            $('#task_dialog').dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
        },

        // when dragndrop finished and datetime changed (internal event dragndrop)
        eventDrop: function(event, delta, revertFunc) {
            daterange = {  // todo pas de var et shadow naming
                start_date: django_date(event['start']),
                end_date: django_date(event['end']),
            };

            // jquery .put doesnt exist.. put wrapper
            put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
                function(data) {}
            );
        },

        // when timestamp resize is finished and time changed
        eventResize: function(event, delta, revertFunc) {
            daterange = {
                start_date: django_date(event['start']),
                end_date: django_date(event['end']),
            };


            put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
            function(data) {}
            );
        },

        drop: function(date) {
            // for low level data callback of external drop, not usefull. called before event receive
        },

        // drop callback only for low level drop data, this gets the external dropped event
        eventReceive: function(event, view) {

            // post a new daterange, but if form is cancelled it's keeped in db
            f_post_daterange(event.start, event.end, function(response) {
                event.id = response['id']; // id of event is id of daterange
                event['many_dateranges'] = event['many_dateranges'].concat([response['id']]);

                task_put = {
                    name: event['title'],
                    many_dateranges: event['many_dateranges'],
                    // fixme le problème c'est que l'objet event ds l'accordeon n'est pas mis a jour tant qu'il
                    //n'y a pas de refresh'
                    // du coup on peut pas ajouter plusieurs daterange d'une mm task en une seule fois
                    // ajoute à la liste des pk de daterange la daterange fraichement postée
                };

                // associe la nouvelle daterange à la task existante
                put("{% url 'api:tasks-list'%}"+event['task_id']+'/', task_put,
                    function(data) {
                        $('#calendar').fullCalendar('updateEvent', event); // here all async modif are commited
                    }
                );

                if (event.is_schedtask == true)  {  // for the first creation of schedtask
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