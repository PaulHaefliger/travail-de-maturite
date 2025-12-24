$fn=30;

difference() {
    union() {
        cube([45, 25, 3], center=true);
        
        translate([18, -6.25, 4]) {
            cylinder(7, 1, 1, center=true);
        }

        translate([-18, -6.25, 4]) {
            cylinder(7, 1, 1, center=true);
        }
    }

    union() {
        translate([10.5, 6.25, 0]) {
            cylinder(5, 2.1, 2.1, center=true);
        }
        
        translate([10.5, -6.25, 0]) {
            cylinder(5, 2.1, 2.1, center=true);
        }
            
        translate([-10.5, 6.25, 0]) {
            cylinder(5, 2.1, 2.1, center=true);
        }

        translate([-10.5, -6.25, 0]) {
            cylinder(5, 2.1, 2.1, center=true);
        }
    }
}
