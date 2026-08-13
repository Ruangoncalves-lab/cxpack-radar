import { NextRequest, NextResponse } from 'next/server';
import { runProspectingPipeline, PipelineProgressEvent } from '@/lib/pipeline';

export const runtime = 'nodejs';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { query, count = 25, region = '' } = body;

    if (!query || typeof query !== 'string') {
      return NextResponse.json({ error: 'Termo de busca é obrigatório' }, { status: 400 });
    }

    const fullQuery = region ? `${query} ${region}` : query;
    const leadLimit = Math.min(Math.max(Number(count) || 25, 5), 100);

    // Configurar ReadableStream para Server-Sent Events (Realtime visual progress bar)
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();
        
        const sendEvent = (data: PipelineProgressEvent) => {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));
        };

        try {
          const results = await runProspectingPipeline(fullQuery, leadLimit, (evt) => {
            sendEvent(evt);
          });

          sendEvent({
            step: 'COMPLETE',
            totalLeads: results.length,
            processedCount: results.length,
            message: 'Prospecção concluída com sucesso!'
          });
        } catch (error: any) {
          sendEvent({
            step: 'ERROR',
            totalLeads: 0,
            processedCount: 0,
            message: error?.message || 'Erro durante o processamento do pipeline'
          });
        } finally {
          controller.close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
      },
    });
  } catch (error: any) {
    return NextResponse.json({ error: error?.message || 'Erro interno no servidor' }, { status: 500 });
  }
}
