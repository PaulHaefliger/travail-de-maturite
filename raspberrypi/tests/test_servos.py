import raspberrypi.servos as servos


def test_get_degrees_pulse_duration():
    assert servos.get_degrees_pulse_duration(0) == 0.0005
    assert servos.get_degrees_pulse_duration(90) == 0.0015
    assert servos.get_degrees_pulse_duration(180) == 0.0025
