var application = function(){
    RobotUtils.onService(function (ALMyService) {
        $("#noservice").hide();
        ALMyService.get().then(function(level) {
            // Find the button with the right level:
            $(".levelbutton").each(function() {
                var button = $(this);
                if (button.data("level") == level) {
                    button.addClass("highlighted");
                    button.addClass("clicked");
                }
            });
            // ... and show all buttons:
            $("#buttons").show();
        });
        $(".levelbutton").click(function() {
            // grey out the button, until we hear back that the click worked.
            var button = $(this);
            var level = button.data("level");
            $(".levelbutton").removeClass("highlighted");
            $(".levelbutton").removeClass("clicked");
            button.addClass("clicked");
            ALMyService.set(level).then(function(){
                button.addClass("highlighted");
            });
        })
    }, function() {
        console.log("Failed to get the service.")
        $("#noservice").show();
    });
};
