angular.module('bumper.view.customer', [
    'bumper.services.common',
    'bumper.services.user'
])
    .controller('customerReviewController', function customerReviewController($location, CommonService, $anchorScroll) {
        var self = this;
        self.isOpen =false;
        self.isDeviceMobile = false;
        Tawk_API = Tawk_API || {};
        $("img.lazy").lazyload();
        self.isDeviceMobile = CommonService.mobileBrowser();
        if(self.isDeviceMobile ){
            try{
                Tawk_API.showWidget();
            }
            catch (e){
                //tawk api not laded
            }
        }
        self.review =
            [


                {
                    'name':'Jawahar Abraham',
                    'rating':'5',
                    'comment':'“I have used their services a few days ago Work Order No 19333. They have done an excellent job. I was really happy with the outcome and they are very customer friendly company. They keep to their schedule and keep you updated. A must try people, who you will go to again and again and recommend your friends. ”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/jawahar_abraham_fb_review.jpg'
                },
                {
                    'name':'Vaibhav Kalway',
                    'rating':'5',
                    'comment':'“Got rid of scratches on my car recently and had a fabulous experience with these guys. Right from the booking, there was lots of communication and transparency on the work being done and prices and they in fact delivered before the promised time. Highly recommended!”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/vaibav-fb-review.jpg'
                },
                {
                    'name':'Himanshu Kumar',
                    'rating':'5',
                    'comment':'“I would have given more stars, if available :) I would like everyone to know this story. To begin with, I wanted a full body dent fix and paint(except roof) for my Swift VDi, Went to Maruti Showroom and those looters quoted 70k for the same.On top of that, full body is not covered under any insurance. I contacted Bumper then and got it done in 29.5k(including rear bumper and tail light replacement).The service was excellent, punctual and warming. I would recommend this to everyone who want to save their hard earned money from going into hands of these looter showrooms”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'Deepak Kumar',
                    'rating':'5',
                    'comment':'“I have booked an online Car Dent repair for my car. Got it repaired hassle free.Here is why,First, prices are consistently lower than the opposition & substantially lower than the authorized dealer.Second, your online portal is so much easier and informative to use, making the whole experience simple with the fixed price.Third, Free pick-up and drop. A great service and thanks.”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'Rishi Chadha',
                    'rating':'5',
                    'comment':'“Awesome place to get dents fixed. Paint work is also Very Good.”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'Ragesh Nair',
                    'rating':'5',
                    'comment':'“Seriously fantastic work done at such a cheap price. I got my i20 painted recently and dents removed. Cool work.”',
                    'source':'Facebook',
                    'medium':'3',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'C​harul',
                    'rating':'5',
                    'comment':'“The app and service were great.Good Customer support staff. Interacted with Divya who connected to workshop mgr for specific details. Painting and bump fixing done well. Suggested to many of my colleagues too !!!”',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'Arun Srinivasan',
                    'rating':'5',
                    'comment':'“Hassle free From pick up at the door to step by step tracking and updates, to final delivery and payment, the best service for a car i have recieved so far. And btw, the dent removal was spotless and I got the interiors cleaned as a bonus!”',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/arun-paystore.jpg'
                },
                {
                    'name':'Hitesh Devnani',
                    'rating':'5',
                    'comment':'“Very prompt service. I gave them my car i20 for scratches and dent repair. They did a wonderful job from picking up the car to returning it. The car came back looking like there was never a scratch in the first place. Very neat job. Very competitive prices as well. Definitely recommend it.',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/hiteshadvani-playstore.jpg'
                },
                {
                    'name':'Prasad Ramachandra​',
                    'rating':'5',
                    'comment':'"Excellent work done by bumper team, they marched the exact colour and their service was good. They stood by their words of pick up and delivery. I was updated on each and every step taken by them on my car."',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/default_user.svg'
                },

                {
                    'name':'​Satadal Bandyopadhyay​',
                    'rating':'4',
                    'comment':'“Tried out bumper for scratch n paint repair, just received the vehicle. Very transparent, communicative. Vehicle delivered back is well finished, cleaning n paint drop removals are done good, can do better given quality of paint work. People using this service needs to know a few details on how much can a dent repair achieve. Bumper u should educate putting pictures in the FAQ and explain warranty process or complain handling process.”',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/default_user.svg'
                },
                {
                    'name':'Chitta ranjan Pradhan',
                    'rating':'5',
                    'comment':'"Awesome job hats off I am really impressed with the service and the way the work is done.Its completely flawless...Good job bumper team way to go cheers ;)"',
                    'source':'Playstore - Android',
                    'medium':'1',
                    'img':'img/chitta-playstore.jpg'
                },
                {
                    'name':'Ashish Kuriyal',
                    'rating':'5',
                    'comment':'“I recently used their service to replace my rear bumper. The work was done very professionally and the price they quoted was best in market. I will recommend everyone to give a try if they looking for such services.”',
                    'source':'App store - iOS',
                    'medium':'2',
                    'img':'img/default_user.svg'

                },
                {
                    'name':'Achyuth Anantapur',
                    'rating':'5',
                    'comment':'“Great work appreciated- keep it up full worthy for money”',
                    'source':'App store - iOS',
                    'medium':'2',
                    'img':'img/default_user.svg'

                },
                {
                    'name':'Ashifullah',
                    'rating':'5',
                    'comment':'“It was really good experience with bumper”',
                    'source':'App store - iOS',
                    'medium':'2',
                    'img':'img/default_user.svg'

                }
            ];
        $(document).ready(function () {
            $("#owl-demo").owlCarousel({
                navigation : true, // Show next and prev buttons
                slideSpeed : 300,
                paginationSpeed : 400,
                singleItem: true
            });

        });
        var old = $location.hash();
        $location.hash('headerTop');
        $anchorScroll();
        $location.hash(old);
        function loadYoutube(){
            var youtube = document.querySelectorAll( ".youtube" );
            for (var i = 0; i < youtube.length; i++) {
                var source = "https://img.youtube.com/vi/"+ youtube[i].dataset.embed +"/sddefault.jpg";
                var image = new Image();
                image.src = source;
                image.addEventListener( "load", function() {
                    youtube[ i ].appendChild( image );
                }( i ) );
                youtube[i].addEventListener( "click", function() {
                    var iframe = document.createElement( "iframe" );
                    iframe.setAttribute( "frameborder", "0" );
                    iframe.setAttribute( "allowfullscreen", "" );
                    iframe.setAttribute( "src", "https://www.youtube.com/embed/"+ this.dataset.embed +"?rel=0&showinfo=0&autoplay=1" );
                    this.innerHTML = "";
                    this.appendChild( iframe );
                } );
            }
        }
        loadYoutube();
    });
