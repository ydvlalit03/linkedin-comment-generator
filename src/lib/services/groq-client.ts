/**
 * Groq API client wrapper
 * Supports text + vision (llama-4-scout)
 */
import Groq from "groq-sdk";
import { createLogger } from "../utils/logger";

const log = createLogger("Groq");

let _client: Groq | null = null;

function getClient(): Groq {
  if (!_client) {
    _client = new Groq({ apiKey: process.env.GROQ_API_KEY || "" });
    log.info("Client initialized");
  }
  return _client;
}

export const MODELS = {
  text: "llama-3.3-70b-versatile",
  vision: "meta-llama/llama-4-scout-17b-16e-instruct",
} as const;

export interface ChatOptions {
  model?: string;
  temperature?: number;
  maxTokens?: number;
  jsonMode?: boolean;
}

/**
 * Text-only chat completion
 */
export async function chat(
  prompt: string,
  options: ChatOptions = {}
): Promise<string> {
  const client = getClient();
  const model = options.model || MODELS.text;

  log.info(`Calling ${model} | temp=${options.temperature ?? 0.7} | json=${!!options.jsonMode} | maxTokens=${options.maxTokens ?? 2000}`);
  log.prompt(`→ ${model}`, prompt);

  const start = Date.now();

  const response = await client.chat.completions.create({
    model,
    temperature: options.temperature ?? 0.7,
    max_completion_tokens: options.maxTokens ?? 2000,
    ...(options.jsonMode
      ? { response_format: { type: "json_object" as const } }
      : {}),
    messages: [{ role: "user", content: prompt }],
  });

  const result = response.choices[0]?.message?.content || "";
  const elapsed = Date.now() - start;
  const usage = response.usage;

  log.info(`Response in ${elapsed}ms | tokens: ${usage?.prompt_tokens || "?"}in → ${usage?.completion_tokens || "?"}out`);
  log.response(`← ${model}`, result);

  return result;
}

/**
 * Vision chat — analyze image with text prompt
 */
export async function analyzeImage(
  imageUrl: string,
  prompt: string,
  options: ChatOptions = {}
): Promise<string> {
  const client = getClient();

  log.info(`Vision call | model=${MODELS.vision}`);
  log.prompt(`→ Vision (image: ${imageUrl.slice(0, 60)}...)`, prompt);

  const start = Date.now();

  const response = await client.chat.completions.create({
    model: MODELS.vision,
    temperature: options.temperature ?? 0.7,
    max_completion_tokens: options.maxTokens ?? 1500,
    ...(options.jsonMode
      ? { response_format: { type: "json_object" as const } }
      : {}),
    messages: [
      {
        role: "user",
        content: [
          { type: "text", text: prompt },
          { type: "image_url", image_url: { url: imageUrl } },
        ],
      },
    ],
  });

  const result = response.choices[0]?.message?.content || "";
  const elapsed = Date.now() - start;

  log.info(`Vision response in ${elapsed}ms`);
  log.response(`← Vision`, result);

  return result;
}

export async function chatWithHistory(
  messages: Array<{ role: "user" | "assistant" | "system"; content: string }>,
  options: ChatOptions = {}
): Promise<string> {
  const client = getClient();
  const model = options.model || MODELS.text;

  log.info(`Multi-turn call | ${messages.length} messages | model=${model}`);

  const response = await client.chat.completions.create({
    model,
    temperature: options.temperature ?? 0.7,
    max_completion_tokens: options.maxTokens ?? 2000,
    ...(options.jsonMode
      ? { response_format: { type: "json_object" as const } }
      : {}),
    messages,
  });

  return response.choices[0]?.message?.content || "";
}
