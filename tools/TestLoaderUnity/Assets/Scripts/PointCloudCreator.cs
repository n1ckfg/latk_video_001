// https://docs.unity3d.com/2019.4/Documentation/Manual/Example-CreatingaBillboardPlane.html

using UnityEngine;

[RequireComponent(typeof(MeshRenderer))]
[RequireComponent(typeof(MeshFilter))]
[ExecuteInEditMode]
public class PointCloudCreator : MonoBehaviour {

    public int numVertices = 1000;

    public void Start() {
        MeshRenderer meshRenderer = GetComponent<MeshRenderer>();
        MeshFilter meshFilter = GetComponent<MeshFilter>();

        Mesh mesh = new Mesh();

        Vector3[] vertices = new Vector3[numVertices];
        Vector3[] normals = new Vector3[numVertices];
        Vector2[] uv = new Vector2[numVertices];
        
        for (int i = 0; i < numVertices; i++) {

            float vertx = Random.Range(-1f, 1f);
            float verty = Random.Range(-1f, 1f);
            float vertz = Random.Range(-1f, 1f);
            vertices[i] = new Vector3(vertx, verty, vertz);

            normals[i] = -Vector3.forward;

            float uvx = Random.Range(0f, 1f);
            float uvy = Random.Range(0f, 1f);
            uv[i] = new Vector2(uvx, uvy);
        }

        mesh.vertices = vertices;
        mesh.normals = normals;
        mesh.uv = uv;

        meshFilter.mesh = mesh;
    }

    /*
    // https://github.com/leon196/PointCloudExporter/blob/master/Assets/Scripts/PointCloudGenerator.cs
		public void Generate (MeshInfos meshInfos, Material materialToApply, MeshTopology topology)
		{

			for (int c = transform.childCount - 1; c >= 0; --c) {
				Transform child = transform.GetChild(c);
				GameObject.DestroyImmediate(child.gameObject);
			}

			int vertexCount = meshInfos.vertexCount;
			int meshCount = (int)Mathf.Ceil(vertexCount / (float)verticesMax);

			meshArray = new Mesh[meshCount];
			transformArray = new Transform[meshCount];

			int index = 0;
			int meshIndex = 0;
			int vertexIndex = 0;

			int resolution = GetNearestPowerOfTwo(Mathf.Sqrt(vertexCount));

			while (meshIndex < meshCount) {

				int count = verticesMax;
				if (vertexCount <= verticesMax) {
					count = vertexCount;
				} else if (vertexCount > verticesMax && meshCount == meshIndex + 1) {
					count = vertexCount % verticesMax;
				}
				
				Vector3[] subVertices = meshInfos.vertices.Skip(meshIndex * verticesMax).Take(count).ToArray();
				Vector3[] subNormals = meshInfos.normals.Skip(meshIndex * verticesMax).Take(count).ToArray();
				Color[] subColors = meshInfos.colors.Skip(meshIndex * verticesMax).Take(count).ToArray();
				int[] subIndices = new int[count];
				for (int i = 0; i < count; ++i) {
					subIndices[i] = i;
				}

				Mesh mesh = new Mesh();
				mesh.bounds = new Bounds(Vector3.zero, Vector3.one * 100f);
				mesh.vertices = subVertices;
				mesh.normals = subNormals;
				mesh.colors = subColors;
				mesh.SetIndices(subIndices, topology, 0);

				Vector2[] uvs2 = new Vector2[mesh.vertices.Length];
				for (int i = 0; i < uvs2.Length; ++i) {
					float x = vertexIndex % resolution;
					float y = Mathf.Floor(vertexIndex / (float)resolution);
					uvs2[i] = new Vector2(x, y) / (float)resolution;
					++vertexIndex;
				}
				mesh.uv2 = uvs2;

				GameObject go = CreateGameObjectWithMesh(mesh, materialToApply, gameObject.name + "_" + meshIndex, transform);
				
				meshArray[meshIndex] = mesh;
				transformArray[meshIndex] = go.transform;

				index += count;
				++meshIndex;
			}
		}
    */

}
