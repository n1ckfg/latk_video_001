float unpackColor(vec4 color) {
	vec4 bitSh = vec4(1.0, 1.0 / 256.0, 1.0 / 65536.0, 1.0 / 16777216.0);
	return dot(color, bitSh);
}

vec3 saturation(vec3 rgb, float adjustment) {
    const vec3 W = vec3(0.2125, 0.7154, 0.0721);
    vec3 intensity = vec3(dot(rgb, W));
    return mix(intensity, rgb, adjustment);
}

const float  _Epsilon = 0.03;

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + _Epsilon)), d / (q.x + _Epsilon), q.x);
}