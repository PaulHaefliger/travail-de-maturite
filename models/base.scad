$fn=30;

cube([41.7, 31.7, 2], center=true);

translate([18.3, 13.1, 3]) {
    cylinder(5.5, 1.2, 1.2, center=true);
}
        
translate([18.3, -13.1, 3]) {
    cylinder(5.5, 1.2, 1.2, center=true);
}
            
translate([-18.3, 13.1, 3]) {
    cylinder(5.5, 1.2, 1.2, center=true);
}

translate([-18.3, -13.1, 3]) {
    cylinder(5.5, 1.2, 1.2, center=true);
}

