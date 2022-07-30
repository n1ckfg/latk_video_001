// https://forum.unity.com/threads/billboard-geometry-shader.169415/
// https://forum.unity.com/threads/dx11-tessalation-vertex-color.164221/

Shader "Nick/LatkVideo" {
	
	Properties {
		_MainTex("Texture", 2D) = "white" {}
		_Scaler("Scaler", float) = 1.0
		_Size("Size", float) = 0.5
		_Brightness("Brightness", float) = 1.0
		_Saturation("Saturation", float) = 1.0
		_SatThresh("Saturation Threshold", float) = 0.85
		_BrightThresh("Bright Threshold", float) = 0.85
		_Epsilon("Epsilon", float) = 0.0000000001
	}

	SubShader {
		Pass {
			Tags { "RenderType"="Opaque" }
			//Blend SrcAlpha One
			LOD 200
		
			CGPROGRAM
			#pragma target 5.0
			#pragma vertex VS_Main
			#pragma fragment FS_Main
			#pragma geometry GS_Main
			#include "UnityCG.cginc" 

			// **************************************************************
			// Data structures												*
			// **************************************************************
			struct GS_INPUT {
				float4	pos			: POSITION;
				float3	normal		: NORMAL;
				float4  color		: COLOR;
				float visibility : TEXCOORD1;
		};

			struct FS_INPUT {
				float4	pos			: POSITION;
				float4  color		: COLOR;
				float visibility : TEXCOORD1;
			};


			// **************************************************************
			// Vars															*
			// **************************************************************

			sampler2D _MainTex;
			float _Scaler;
			float _Size;
			float _Brightness;
			float _Saturation;
			float _BrightThresh;
			float _SatThresh;
			float _Epsilon;
			float4x4 _VP;

			// **************************************************************
			// Shader Programs												*
			// **************************************************************

			float rgbToHue(float3 c) {
				float4 K = float4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
				float4 p = lerp(float4(c.bg, K.wz), float4(c.gb, K.xy), step(c.b, c.g));
				float4 q = lerp(float4(p.xyw, c.r), float4(c.r, p.yzx), step(p.x, c.r));

				float d = q.x - min(q.w, q.y);

				float3 result = float3(abs(q.z + (q.w - q.y) / (6.0 * d + _Epsilon)), d / (q.x + _Epsilon), q.x);

				return result.g > _SatThresh && result.b > _BrightThresh ? result.r : 0.0;
			}

			float3 saturation(float3 rgb, float adjustment) {
				float3 W = float3(0.2125, 0.7154, 0.0721);
				float intensity = dot(rgb, W);
				float3 intensity3 = float3(intensity, intensity, intensity);
				return lerp(intensity, rgb, adjustment);
			}

			// Vertex Shader ------------------------------------------------
			GS_INPUT VS_Main(appdata_full v) {
				GS_INPUT output = (GS_INPUT)0;

				float2 uvRgb = float2(v.texcoord.x * 0.5, v.texcoord.y - 0.5);
				float2 uvX = float2(0.5 + v.texcoord.x * 0.5, v.texcoord.y - 0.5);
				float2 uvY = float2(0.5 + v.texcoord.x * 0.5, v.texcoord.y);
				float2 uvZ = float2(v.texcoord.x * 0.5, v.texcoord.y);

				float posX = rgbToHue(tex2Dlod(_MainTex, float4(uvX, 0, 0))	);
				float posY = rgbToHue(tex2Dlod(_MainTex, float4(uvY, 0, 0)));
				float posZ = rgbToHue(tex2Dlod(_MainTex, float4(uvZ, 0, 0)));

				output.visibility = posX == 0.0 || posY == 0.0 || posZ == 0.0 ? 0.0 : 1.0;

				v.vertex.xyz = float3(posX, posZ, posY) * _Scaler;

				output.pos =  mul(unity_ObjectToWorld, v.vertex);
				output.normal = v.normal;

				float4 col = tex2Dlod(_MainTex, float4(uvRgb, 0, 0));
				output.color = col; // v.color;

				return output;
			}

			// Geometry Shader -----------------------------------------------------
			[maxvertexcount(4)]
			void GS_Main(point GS_INPUT p[1], inout TriangleStream<FS_INPUT> triStream) {
				float3 up = float3(0, 1, 0);
				float3 look = _WorldSpaceCameraPos - p[0].pos;
				look.y = 0;
				look = normalize(look);
				float3 right = cross(up, look);
					
				float halfS = 0.5f * _Size;
							
				float4 v[4];
				v[0] = float4(p[0].pos + halfS * right - halfS * up, 1.0f);
				v[1] = float4(p[0].pos + halfS * right + halfS * up, 1.0f);
				v[2] = float4(p[0].pos - halfS * right - halfS * up, 1.0f);
				v[3] = float4(p[0].pos - halfS * right + halfS * up, 1.0f);

				float4x4 vp;
				#if UNITY_VERSION >= 560 
				vp = mul(UNITY_MATRIX_MVP, unity_WorldToObject);
				#else 
				#if UNITY_SHADER_NO_UPGRADE 
				vp = mul(UNITY_MATRIX_MVP, unity_WorldToObject);
				#endif
				#endif
				FS_INPUT pIn;
				pIn.visibility = p[0].visibility;

				pIn.pos = mul(vp, v[0]);
				pIn.color = p[0].color;
				triStream.Append(pIn);

				pIn.pos =  mul(vp, v[1]);
				pIn.color = p[0].color;
				triStream.Append(pIn);

				pIn.pos =  mul(vp, v[2]);
				pIn.color = p[0].color;
				triStream.Append(pIn);

				pIn.pos =  mul(vp, v[3]);
				pIn.color = p[0].color;
				triStream.Append(pIn);
			}

			// Fragment Shader -----------------------------------------------
			float4 FS_Main(FS_INPUT input) : COLOR{
				if (input.visibility == 0.0) discard;

				return float4(saturation(input.color.xyz, _Saturation) * _Brightness, 1.0);
			}

			ENDCG
		}
	} 

}
