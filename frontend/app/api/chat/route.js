export async function POST(req) {
  try {
    console.log("[API/CHAT] Requisição recebida"); // Log da requisição recebida
    const { messages } = await req.json();
    console.log("[API/CHAT] Corpo da requisição:", messages); // Log do corpo da requisição

    const proxyUrl = process.env.PROXY_URL || "http://proxy:5050/api/chat";
    console.log(`[API/CHAT] Chamando proxy em: ${proxyUrl}`); // Log da URL do proxy

    // Ajustando o formato do corpo da requisição para incluir o model
    const resposta = await fetch(proxyUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "default",
        messages: messages,
      }),
    });

    console.log(`[API/CHAT] Resposta do proxy: status=${resposta.status}`); // Log do status da resposta

    if (!resposta.ok) {
      console.error(
        "[API/CHAT] Erro ao consultar o proxy:",
        resposta.status,
        resposta.statusText
      ); // Log de erro detalhado
      return Response.json(
        { erro: "Erro ao consultar o proxy." },
        { status: 500 }
      );
    }

    const data = await resposta.json();
    console.log("[API/CHAT] Resposta do proxy (JSON):", data); // Log da resposta JSON
    return Response.json(data);
  } catch (error) {
    console.error("[API/CHAT] Erro interno no servidor:", error); // Log de erro interno
    return Response.json(
      { erro: "Erro interno no servidor." },
      { status: 500 }
    );
  }
}
