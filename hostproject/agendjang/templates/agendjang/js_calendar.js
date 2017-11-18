// template dynamic js, why not,
$(document).ready(function() {  // called when page completly loaded

            // helper: view-source:https://fullcalendar.io/js/fullcalendar-3.7.0/demos/agenda-views.html

            $('#calendar').fullCalendar({
                // put your options and callbacks here
                editable: true,  // event on the calendar can be modified
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay,listWeek'
                },


                // todo load by ajax the existing tasks with timestamp




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
//                        url: 'http://google.com/',  // overides click event
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

//                    alert($('#calendar').fullCalendar('clientEvents')[1]['title']);  // retourne un tableau d'event, on prend le premier

                },


                // quand on clique sur un event..
                eventClick: function(event) { // on aussi avoir la position de la souris, la vue etc..
                    alert(event['title'] + ' event clicked: startdate ' + event['start']);
                },

                // when dragndrop finished and datetime changed
                eventDrop: function(event, delta, revertFunc) {
                    alert(event['title'] + ' datetime changed: ' + event['start'] );
                    // todo update the task by ajax
                },

                // when timestamp resize is finished and time changed
                eventResize: function(event, delta, revertFunc) {
                    alert(event['title'] + ' datetime resized: ' + event['start'] );
                }


            })

        });