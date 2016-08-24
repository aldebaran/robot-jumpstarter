var application = function(){
    RobotUtils.onService(function(ALTextToSpeech) {
        // Bind button callbacks
        $(".bleeper").click(function() {
            ALTextToSpeech.say($(this).html());
        });
    });
}
