export async function POST(req) {
  try {
    console.log("[API/EMBEDDINGS] Receiving text block...");
    const { text } = await req.json();

    // Match the exact API message format
    const requestBody = {
      ids: [
        Date.now().toString(), // unique_id
      ],
      documents: [
        text, // text to embed
      ],
      metadatas: [
        {
          origin: "user_input",
        },
      ],
    };

    console.log("[API/EMBEDDINGS] Request body:", JSON.stringify(requestBody));

    const proxyUrl =
      process.env.PROXY_URL || "http://proxy:5050/api/embeddings";
    const response = await fetch(proxyUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[API/EMBEDDINGS] Error response:", {
        status: response.status,
        body: errorText,
      });

      return Response.json(
        { error: `Failed to process text (${response.status})` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return Response.json({
      message: "Text processed successfully",
      ...data,
    });
  } catch (error) {
    console.error("[API/EMBEDDINGS] Error:", error);
    return Response.json({ error: "Internal server error" }, { status: 500 });
  }
}
