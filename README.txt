2021 Computer Graphics
PA2 - Cow Roller Coaster
Author - Yeonggwon Pyo
Last Edit - 2021-06-14
#############################################

Modified file: SimpleScene.py

body:
<global_variables>
    cow_ctrl_pts : list of cow control points.
    is_picking : boolean variable for checking it is on picking state.
    animStartTime : represent the start time to animate cow.

    NUM_TURN : number of turning(animating) cow.
</global_variables>

<functions>
    getSplinePos(animTime) : added newly
        get p(t) value at t = animTime.
        used Catmull-Rom Matrix to approximate points on B-spline basis.
        returns [t^3 t^2 t 1] @ Catmull_Rom_Mtrx @ [p0 p1 p2 p3].T

    actCow(animTime)
        represents rotation and translation of cow.
        use camera matrix of pipeline progress because of local frame.
    
    display() - TODO
        while is_picking is False, it means that user has selected 6 cow's positions.
        as finishing, changes is_picking state into True so that convert initial state.
    
    set4TurnCow() : added newly
        as soon as user selected 6 positions of cow, this function is called.
        sets cow_ctrl_pts with NUM_TURN times for representing to act NUM_TURN times.
        and append initial point to go back initial position.

    onMouseButton(window,button, state, mods)
        if user clicked mouse left button, make copy of cow to select next position of it.
        when user just clicked mouse left buttion once, drag mode is changed into V_DRAG.
        in this state, user can drag the cow with vertical side only.
        after dragged, the state parameter be GLFW_UP and then drag mode is changed
        into H_DRAG.
        after chose 6 positions, convert is_picking into False and call set4TurnCow().

    onMouseDrag(window, x, y) - TODO
        after user select a position, isDrag be V_DRAG and set vertical position of cow
        along specific x and z.
        it was refered with horizontal dragging

    main()
        the title of window changed with my student ID and PA number.
        originally, it was "modern opengl example"
</function>