Shader "Nick/Latk-Video" {

    Properties {
        _MainTex ("Texture", 2D) = "white" {}
		_Size("Size", Range(0, 3)) = 0.5
		//_Brightness("Brightness", Range(1, 200)) = 10.0
		satThresh ("Saturation Threshold", Float) = 0.5 		// orig 0.5 or 0.85
		brightThresh ("Brightness Threshold", Float) = 0.5 	// orig 0.5 or 0.85 or 0.9
		epsilon ("Epsilon", Float) = 0.03 // orig 1.0e-10 or 0.0000000001 or orig 0.03
		visibilityThreshold ("Visibility Threshold", Float) = 0.99
	}

    SubShader {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass {
            CGPROGRAM
			#pragma require geometry
			#pragma vertex vert
            #pragma fragment frag
			#pragma geometry geom

            #include "UnityCG.cginc"

			struct appdata {
				float4 vertex : POSITION;
				UNITY_VERTEX_INPUT_INSTANCE_ID
			};

			struct v2g {
				float4 vertex : POSITION;
				float2 uv : TEXCOORD0;
				UNITY_VERTEX_OUTPUT_STEREO
			};

			struct g2f {
				float4 pos : SV_POSITION;
				float2 uv : TEXCOORD0;
				UNITY_VERTEX_OUTPUT_STEREO
			};

            sampler2D _MainTex;
            float4 _MainTex_ST;
			float _Size;
			//float _Brightness;
			float satThresh, brightThresh, epsilon, visibilityThreshold;
			//float meshDensityVal = 2048.0;
			float2 meshDensity = float2(2048.0, 2048.0); //meshDensityVal, meshDensityVal);
			int numNeighbors = 4; // orig 8
			int numDudNeighborsThreshold = 3; // int(float(numNeighbors) * 0.75);

			float rgbToHue(float3 c) {
				float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
				float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
				float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));

				float d = q.x - min(q.w, q.y);

				float3 result = float3(abs(q.z + (q.w - q.y) / (6.0 * d + epsilon)), d / (q.x + epsilon), q.x);

				return result.g > satThresh && result.b > brightThresh ? result.r : 0.0;
			}

			float depthForPoint(float2 uv) {
				return rgbToHue(tex2Dlod(_MainTex, float4(uv, 0, 0)).rgb);
			}

			float3 saturation(float3 rgb, float adjustment) {
				float3 W = float3(0.2125, 0.7154, 0.0721);
				float3 intensity = dot(rgb, W);
				return lerp(intensity, rgb, adjustment);
			}

			float calculateVisibility(float depth, float2 uv) {
				float visibility = 1.0;
				float2 textureStep = 1.0 / meshDensity;

				float neighborDepths[4];

				neighborDepths[0] = depthForPoint(uv + float2(0.0, textureStep.y));
				neighborDepths[1] = depthForPoint(uv + float2(textureStep.x, 0.0));
				neighborDepths[2] = depthForPoint(uv + float2(0.0, -textureStep.y));
				neighborDepths[3] = depthForPoint(uv + float2(-textureStep.x, 0.0));
				//neighborDepths[4] = depthForPoint(uv + float2(-textureStep.x, -textureStep.y));
				//neighborDepths[5] = depthForPoint(uv + float2(textureStep.x, textureStep.y));
				//neighborDepths[6] = depthForPoint(uv + float2(textureStep.x, -textureStep.y));
				//neighborDepths[7] = depthForPoint(uv + float2(-textureStep.x, textureStep.y));

				// Search neighbor verts in order to see if we are near an edge.
				// If so, clamp to the surface closest to us.
				int numDudNeighbors = 0;
				if (depth < epsilon || (1.0 - depth) < epsilon) {
					float nearestDepth = 1.0;
					for (int i = 0; i < numNeighbors; i++) {
						float depthNeighbor = neighborDepths[i];
						if (depthNeighbor >= epsilon && (1.0 - depthNeighbor) > epsilon) {
							if (depthNeighbor < nearestDepth) {
								nearestDepth = depthNeighbor;
							}
						}
						else {
							numDudNeighbors++;
						}
					}

					depth = nearestDepth;
					visibility = 0.8;

					// Blob filter
					if (numDudNeighbors > numDudNeighborsThreshold) {
						visibility = 0.0;
					}
				}

				// Internal edge filter
				float maxDisparity = 0.0;

				for (int i = 0; i < numNeighbors; i++) {
					float depthNeighbor = neighborDepths[i];
					if (depthNeighbor >= epsilon && (1.0 - depthNeighbor) > epsilon) {
						maxDisparity = max(maxDisparity, abs(depth - depthNeighbor));
					}
				}

				visibility *= 1.0 - maxDisparity;

				return visibility;
			}
           
			v2g vert(appdata_full v) {
				v2g o;
				UNITY_SETUP_INSTANCE_ID(v);
				UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);

				float2 uvX = float2(0.5 + v.texcoord.x * 0.5, 0.5 + v.texcoord.y * 0.5);
				float2 uvY = float2(0.5 + v.texcoord.x * 0.5, v.texcoord.y * 0.5);
				float2 uvZ = float2(v.texcoord.x * 0.5, v.texcoord.y * 0.5);

				float posX = depthForPoint(uvX);
				float posY = depthForPoint(uvY);
				float posZ = depthForPoint(uvZ);

				float visX = calculateVisibility(posX, uvX);
				float visY = calculateVisibility(posY, uvY);
				float visZ = calculateVisibility(posZ, uvZ);

				//visibility = visX < visibilityThreshold || visY < visibilityThreshold || visZ < visibilityThreshold ? 0.0 : 1.0;

				float3 newPosition = float3(posX, posY, posZ);

				o.vertex = mul(unity_WorldToObject, newPosition);
				o.uv = v.texcoord;

                return o;
            }

			[maxvertexcount(3)]
			void geom(triangle v2g IN[3], inout TriangleStream<g2f> tristream) {
				g2f o;

				float3 up = float3(0, 1, 0);
				float3 look = _WorldSpaceCameraPos - IN[0].vertex;
				look.y = 0;
				look = normalize(look);
				float3 right = cross(up, look);

				float halfS = 0.5f * _Size;

				float4 v[3];
				v[0] = float4(IN[0].vertex + (halfS * 2) * right - (halfS * 2) * up, 1.0f);
				//v[0] = float4(IN[0].vertex + halfS * right - halfS * up, 1.0f);
				v[1] = float4(IN[0].vertex + halfS * right + halfS * up, 1.0f);
				v[2] = float4(IN[0].vertex - halfS * right - halfS * up, 1.0f);

				float4x4 vp;
#if UNITY_VERSION >= 560 
				vp = mul(UNITY_MATRIX_MVP, unity_WorldToObject);
#else 
#if UNITY_SHADER_NO_UPGRADE 
				vp = mul(UNITY_MATRIX_MVP, unity_WorldToObject);
#endif
#endif

				o.pos = mul(vp, v[0]);
				o.uv = IN[0].uv; // float2(1.0f, 0.0f);
				tristream.Append(o);

				o.pos = mul(vp, v[1]);
				o.uv = IN[0].uv; //float2(1.0f, 1.0f);
				tristream.Append(o);

				o.pos = mul(vp, v[2]);
				o.uv = IN[0].uv; //float2(0.0f, 0.0f);
				tristream.Append(o);
			}

			fixed4 frag(g2f i) : SV_Target{
				float2 uvRgb = float2(i.uv.x * 0.5, 0.5 + i.uv.y * 0.5);
				fixed4 col = tex2D(_MainTex, uvRgb);
				return fixed4(saturation(col.xyz, 1.2), 1.0);
            }
            ENDCG
        }
    }
}

/*
// https://stackoverflow.com/questions/18453302/how-do-you-pack-one-32bit-int-into-4-8bit-ints-in-glsl-webgl
// https://stackoverflow.com/questions/6893302/decode-rgb-value-to-single-float-without-bit-shift-in-glsl
// https://github.com/processing/processing4/blob/master/core/src/processing/core/PApplet.java#L9800
// https://marcodiiga.github.io/encoding-normalized-floats-to-rgba8-vectors
// https://blog.actorsfit.com/a?ID=00001-0fe9ed1e-0483-4571-ab97-894fecb35983
// https://vrdust.org.uk/wp-content/plugins/vcdustbackground/includes/dust_shaders.js
// https://github.com/juniorxsound/Depthkit.js
// https://github.com/simeonradivoev/kinect-hue-depth-encoding
// https://github.com/andybiar/Z-Depth-Image-Converter/
*/

/*
varying vec2 vUv;
varying float visibility;
uniform sampler2D tex;

// * * * * * * * * * * * * * * * * *
const float satThresh = 0.5; 		// orig 0.5 or 0.85
const float brightThresh = 0.5; 	// orig 0.5 or 0.85 or 0.9
const float epsilon = 1.0e-10; // orig 1.0e-10 or 0.0000000001 or orig 0.03
const float visibilityThreshold = 0.99;
// * * * * * * * * * * * * * * * * *

const float meshDensityVal = 2048.0;
const vec2 meshDensity = vec2(meshDensityVal, meshDensityVal);
const int numNeighbors = 4; // orig 8
const int numDudNeighborsThreshold = int(float(numNeighbors) * 0.75);

float rgbToHue(vec3 c) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

	float d = q.x - min(q.w, q.y);

	vec3 result = vec3(abs(q.z + (q.w - q.y) / (6.0 * d + epsilon)), d / (q.x + epsilon), q.x);

	return result.g > satThresh && result.b > brightThresh ? result.r : 0.0;
}

float depthForPoint(vec2 uv) {
	return rgbToHue(texture2D(tex, uv).rgb);
}

float calculateVisibility(float depth, vec2 uv) {
	float visibility = 1.0;
	vec2 textureStep = 1.0 / meshDensity;
	float neighborDepths[numNeighbors];
	neighborDepths[0] = depthForPoint(uv + vec2(0.0,  textureStep.y));
	neighborDepths[1] = depthForPoint(uv + vec2(textureStep.x, 0.0));
	neighborDepths[2] = depthForPoint(uv + vec2(0.0, -textureStep.y));
	neighborDepths[3] = depthForPoint(uv + vec2(-textureStep.x, 0.0));
	//neighborDepths[4] = depthForPoint(uv + vec2(-textureStep.x, -textureStep.y));
	//neighborDepths[5] = depthForPoint(uv + vec2(textureStep.x,  textureStep.y));
	//neighborDepths[6] = depthForPoint(uv + vec2(textureStep.x, -textureStep.y));
	//neighborDepths[7] = depthForPoint(uv + vec2(-textureStep.x,  textureStep.y));

	// Search neighbor verts in order to see if we are near an edge.
	// If so, clamp to the surface closest to us.
	int numDudNeighbors = 0;
	if (depth < epsilon || (1.0 - depth) < epsilon) {
		float nearestDepth = 1.0;
		for (int i=0; i<numNeighbors; i++) {
			float depthNeighbor = neighborDepths[i];
			if (depthNeighbor >= epsilon && (1.0 - depthNeighbor) > epsilon) {
				if (depthNeighbor < nearestDepth) {
					nearestDepth = depthNeighbor;
				}
			} else {
				numDudNeighbors++;
			}
		}

		depth = nearestDepth;
		visibility = 0.8;

		// Blob filter
		if (numDudNeighbors > numDudNeighborsThreshold) {
			visibility = 0.0;
		}
	}

	// Internal edge filter
	float maxDisparity = 0.0;

	for (int i=0; i<numNeighbors; i++) {
		float depthNeighbor = neighborDepths[i];
		if (depthNeighbor >= epsilon && (1.0 - depthNeighbor) > epsilon) {
			maxDisparity = max(maxDisparity, abs(depth - depthNeighbor));
		}
	}

	visibility *= 1.0 - maxDisparity;

	return visibility;
}

void main() {
	gl_PointSize = 6.0;

	vUv = uv;
	vec2 uvX = vec2(0.5 + uv.x * 0.5, 0.5 + uv.y * 0.5);
	vec2 uvY = vec2(0.5 + uv.x * 0.5, uv.y * 0.5);
	vec2 uvZ = vec2(uv.x * 0.5, uv.y * 0.5);

	float posX = depthForPoint(uvX);
	float posY = depthForPoint(uvY);
	float posZ = depthForPoint(uvZ);

	float visX = calculateVisibility(posX, uvX);
	float visY = calculateVisibility(posY, uvY);
	float visZ = calculateVisibility(posZ, uvZ);
	visibility = visX < visibilityThreshold || visY < visibilityThreshold || visZ < visibilityThreshold ? 0.0 : 1.0;

	vec3 newPosition = vec3(posX, posY, posZ);

	gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
}
*/

/*
// https://github.com/CesiumGS/cesium/blob/main/Source/Shaders/Builtin/Functions/saturation.glsl

varying vec2 vUv;
varying float visibility;
uniform sampler2D tex;

vec3 saturation(vec3 rgb, float adjustment) {
	const vec3 W = vec3(0.2125, 0.7154, 0.0721);
	vec3 intensity = vec3(dot(rgb, W));
	return mix(intensity, rgb, adjustment);
}

void main() {
	vec2 uvRgb = vec2(vUv.x * 0.5, 0.5 + vUv.y * 0.5);
	vec4 col = texture2D(tex, uvRgb);

	if (visibility < 0.9) discard;

	gl_FragColor = vec4(saturation(col.xyz, 1.2), 0.25);
}
*/