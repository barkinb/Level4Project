# User manual 

This application works by entering the names of the axes on the nomogram, selecting Bezier control points for each axis, drawing a Bezier curve to 
create the representation for the axis. Then you add axis values for 4 points on each axis and the program will be able to know what the value for a variable is at any point.
Then you can add probability distributions and add an isopleth to interact with the nomogram. 

You can also load and save your nomogram configuration as a JSON. Please save the JSON in the same directory as the nomogram. 

Example: BMI nomogram 

1) First, you can use the Select Axis dropdown menu to enter the names for an axis (shortcut : "ctrl - n"). 
2) Then, please click the "Pick Control Point" button to select a point at the start and end point for the axis or press ""ctrl - C", and click on the "Draw" icon or press "ctrl - B" to draw a Bezier curve between those control points. 

3) You should see an overlay on the axis. You can freely move the points you just created to move the shape of the line or curve so that it fits the shape of the axis on the nomogram. 

4) After you have fit the line or curve on the axis , please click on the "Capture Coordinate" button or press "ctrl -A", for every point . Select as many points and enter their values as you see until there is an accurate estimate of the values of the axis on the Canvas. This is so that the application can predict what the value is at any point on an axis. 

Please repeat steps 1-4 for every axis' on the nomogram. 

The finished version should look like this: https://    lists.office.com/Images/6e725c29-763a-4f50-81f2-2e254f0133c8/78af8b25-4c76-4920-8022-272796441d2b/T28SUMVLXUEXCYFPMI8DP28XOT/51269f75-c4f4-4cf4-bb33-06e453efb435

For height, please insert a normal distribution by typing Normal(175,7.5) into the text field, ensuring that you have the height axis selected. Then press 'Save Distribution'. 

After you have added a distribution, it will visualise the probability density or mass function on the axis. 

For weight, please insert a normal distribution by typing Normal(68,10) into the text field, ensuring that you have the weight axis selected. Then press 'Save Distribution'. 

Now, you can click on the "Create Isopleth" button and interact with the nomogram. 