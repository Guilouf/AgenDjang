// template dynamic js, why not,
$(document).ready(function() {  // called when page completly loaded

            // helper: view-source:https://fullcalendar.io/js/fullcalendar-3.7.0/demos/agenda-views.html

            // wrapper for ajax put
            function put(url_, data_, callback_) {
                $.ajax({  // fixme csrf, faut pas envoyer de cookies
                    url: url_,  // leave trailing /
                    type: 'PUT',
                    contentType: 'application/json',
                    data: JSON.stringify(data_),
                    success: callback_,
                });
            };

            $('#calendar').fullCalendar({
                // put your options and callbacks here
                editable: true,  // event on the calendar can be modified
                slotLabelFormat: 'H(:mm)',  //24h date format
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay,listWeek'
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

                            },
                        {% endfor %}
                    {% endfor %}
                ],




                // when we clic a day..
                dayClick: function(datee) {  // on rajoute comme arg ce que l'on veut recup ds la callback, rien sinon
                    alert(datee + 'has been clicked!'); // 1970.. et que la date du jour


                    var event1= {
//                        start: "{% now 'Y-m-d' %}",  // tag django today date ~'2017-11-17'
                        //mais on utilise pas ca mais la date js

                        // if start == end => all day event (no hour set) fixme c'est vrai ca ??
                        // 2 event with same id => repeated

                        start: datee,
                        end: datee,
                    };


                    // appel get en ajax
                    // detail or list as suffixe for drf to get the rigth view, api: is the router name
//                    $.getJSON("{% url 'api:tasks-detail' 1%}", function(result){ // comment passer le 1 au tag ? hein ?
                    $.getJSON("{% url 'api:tasks-list'%}1", function(result){ // ben comme d'hab on triche

                        event1['title'] = result['name'];  // result reppr le json du get

                        // ajout de event1
                        $('#calendar').fullCalendar( 'renderEvent', event1, true); //true c'est pour qu'il reste a chaque changement de mois etc..
                    });


                    var task_post = {
                        name: "ouloulou",

                    };

                    // postJSON does not exist.. => extra param viva js, jquery
                    $.post("{% url 'api:tasks-list'%}", task_post, function(response) {
                        alert("truc posted"); // todo et pour les erreurs ?
                    }, 'json');


                },


                // quand on clique sur un event..
                eventClick: function(event) { // on aussi avoir la position de la souris, la vue etc..
                    // fixme c'est propre mais c pas de l'ajax, faut reload la page a chaque post..
                    // en revanche, ca va bien ac les event init via django template..
                    $('#task_dialog').load("update_task/"+event['task_id']);  // relative url, resolver useless
                    $('#task_dialog').dialog({width: 'auto'});  // show jquery ui dialog, fit to loaded
                },

                // when dragndrop finished and datetime changed
                eventDrop: function(event, delta, revertFunc) {
                    daterange = {
                        start_date: event['start'],
                        end_date: event['end'],
                    };

                    // jquery .put doesnt exist.. put wrapper
                    put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
                        function(data) { alert('drop put success!!!');}
                    );
                },

                // when timestamp resize is finished and time changed
                eventResize: function(event, delta, revertFunc) {
                    daterange = {
                        start_date: event['start'],
                        end_date: event['end'],
                    };


                    put("{% url 'api:dateranges-list'%}"+event['id']+'/', daterange,
                    function(data) { alert('resize put success!!!');}
                    );

                }


            })

        });