Shader "Nick/TestLoader" {
    
    Properties {
        _MainTex ("Texture", 2D) = "white" {}
		_Scaler("Scaler", float) = 1.0
	}
 
    SubShader {
        Tags { "RenderType"="Opaque" }
        Lighting Off 
        LOD 300
 
        CGPROGRAM
        #pragma surface surf Lambert vertex:disp nolightmap
        #pragma target 3.0
        #pragma glsl
 
		sampler2D _MainTex;
		float _Scaler;

        struct Input {
			float2 uv_MainTex; //(1.0, 1.0) U, V
        };

		float unpackColor(float3 color) {
			float3 bitSh = float3(1.0, 1.0 / 256.0, 1.0 / 65536.0); // , 1.0 / 16777216.0);
			return dot(color, bitSh);
		}

		void disp(inout appdata_full v) {
			float2 uvX = float2(0.5 + v.texcoord.x * 0.5, v.texcoord.y - 0.5);
			float2 uvY = float2(0.5 + v.texcoord.x * 0.5, v.texcoord.y);
			float2 uvZ = float2(v.texcoord.x * 0.5, v.texcoord.y);

			float posX = unpackColor(tex2Dlod(_MainTex, float4(uvX, 0, 0)));
			float posY = unpackColor(tex2Dlod(_MainTex, float4(uvY, 0, 0)));
			float posZ = unpackColor(tex2Dlod(_MainTex, float4(uvZ, 0, 0)));

			v.vertex.xyz = float3(posX, posZ, posY) * _Scaler;
		}
	
		void surf(Input IN, inout SurfaceOutput o) {
			float2 uvRgb = float2(IN.uv_MainTex.x * 0.5, IN.uv_MainTex.y - 0.5);

			fixed4 mainTex = tex2D(_MainTex, uvRgb);
			o.Emission = mainTex.rgb;
		}
        
        ENDCG
    }

    FallBack "Diffuse"

}