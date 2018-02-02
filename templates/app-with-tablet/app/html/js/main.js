var KEY_TABLETSETATE = "app-with-tablet/TabletState";

function updateTabletState(stateJson) {
    var state = JSON.parse(stateJson);
    if (state.title) {
        $("#biglabel").show();
        $("#biglabel").html(state.title);
    } else {
        $("#biglabel").hide();
    }
}

RobotUtils.onService(function (ALMemory) {
    ALMemory.getData(KEY_TABLETSETATE).then(updateTabletState);
    //updateTabletState('{"title": "TEST"}');
});
RobotUtils.subscribeToALMemoryEvent(KEY_TABLETSETATE, updateTabletState);
