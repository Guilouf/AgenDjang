// dynamic js, why not,
$(document).ready(function() {

            // page is now ready, initialize the calendar...

            $('#calendar').fullCalendar({
                // put your options and callbacks here
                editable: true,

                //les evenements:
                // donc on peut les mettre à l'arrache depuis template
                events: [{
                    title: "merde",
                    start: '2017-10-21',
                    end: '2017-10-22',
                    },],



                dayClick: function() {
                    //alert('a day has been clicked!');
                    /*
                    $.getJSON("http://127.0.0.1:8000/api/tasks/1/", function(result){
                        $.each(result, function(i, field){
                            alert(field);
                        });
                    });
                    */
                    /*
                    $.getJSON("http://127.0.0.1:8000/api/tasks/1/", function(result){
                        alert(result['name']);
                    });
                    */

                    // je crois que j'ai pas compris le principe de l'ajax en fait...



                    var event1= {
                        //title: "putain de merde",
                        //title: $.get('http://127.0.0.1:8000/api/tasks/1/', function(data) { alert(data.attr('name'))}),
                        //title: $.get('http://127.0.0.1:8000/api/tasks/1/'),

                        start: '2017-10-23',
                        end: '2017-10-24',
                    };

                    // appel ajax
                    $.getJSON("http://127.0.0.1:8000/api/tasks/1/", function(result){
                        event1['title'] = result['name'];
                        // ajout de event1
                        $('#calendar').fullCalendar( 'renderEvent', event1, true);
                    });


                }
            })

        });