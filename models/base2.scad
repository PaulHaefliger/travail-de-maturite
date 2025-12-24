translate([22.8, -8, -3]) {
    cube([2, 10, 8], center=true);
}

translate([-22.8, 8, -3]) {
    cube([2, 10, 8], center=true);
}

difference() {
    union() {
        cube([45, 35, 2], center=true);
        }
        cube([42, 32, 4], center=true);
    
    }