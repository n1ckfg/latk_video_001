// https://forum.unity.com/threads/billboard-geometry-shader.169415/
// https://forum.unity.com/threads/dx11-tessalation-vertex-color.164221/

Shader "Nick/LED Display" {
	
	Properties {
		_Size("Size", Range(0, 3)) = 0.5
		_Brightness("Brightness", Range(1, 200)) = 10.0
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
			};

			struct FS_INPUT {
				float4	pos			: POSITION;
				float4  color		: COLOR;
			};


			// **************************************************************
			// Vars															*
			// **************************************************************

			float _Size;
			float _Brightness;
			float4x4 _VP;

			// **************************************************************
			// Shader Programs												*
			// **************************************************************

			// Vertex Shader ------------------------------------------------
			GS_INPUT VS_Main(appdata_full v) {
				GS_INPUT output = (GS_INPUT)0;

				output.pos =  mul(unity_ObjectToWorld, v.vertex);
				output.normal = v.normal;
				output.color = v.color;

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
			float4 FS_Main(FS_INPUT input) : COLOR {
				return input.color * _Brightness;
			}

			ENDCG
		}
	} 

}
