import crypto from "node:crypto";
import type { Config, Context } from "@netlify/functions";

const GAS_WEBHOOK_URL =
  "https://script.google.com/macros/s/AKfycby4Tn3NHhyIVd_3gQzGT6bfF2EP9Q6bZ2IMLET5BE_ttVZCLBlC8yz5JpXOS_JAE6pi/exec";

const toleranceSeconds = 300;

function timingSafeEqual(a: string, b: string) {
  const aBuffer = Buffer.from(a);
  const bBuffer = Buffer.from(b);

  return aBuffer.length === bBuffer.length && crypto.timingSafeEqual(aBuffer, bBuffer);
}

function verifyStripeSignature(rawBody: string, signatureHeader: string, secret: string) {
  const parts = signatureHeader.split(",").reduce<Record<string, string[]>>((acc, part) => {
    const [key, value] = part.split("=");
    if (!key || !value) return acc;

    acc[key] = acc[key] || [];
    acc[key].push(value);
    return acc;
  }, {});

  const timestamp = parts.t && parts.t[0];
  const signatures = parts.v1 || [];

  if (!timestamp || signatures.length === 0) {
    return false;
  }

  const age = Math.abs(Math.floor(Date.now() / 1000) - Number(timestamp));
  if (!Number.isFinite(age) || age > toleranceSeconds) {
    return false;
  }

  const expected = crypto
    .createHmac("sha256", secret)
    .update(`${timestamp}.${rawBody}`, "utf8")
    .digest("hex");

  return signatures.some((signature) => timingSafeEqual(signature, expected));
}

export default async (req: Request, context: Context) => {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const rawBody = await req.text();
  const webhookSecret = Netlify.env.get("STRIPE_WEBHOOK_SECRET");
  const signatureHeader = req.headers.get("stripe-signature") || "";

  if (webhookSecret && !verifyStripeSignature(rawBody, signatureHeader, webhookSecret)) {
    return new Response("Invalid Stripe signature", { status: 400 });
  }

  context.waitUntil(
    fetch(GAS_WEBHOOK_URL, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: rawBody,
    }).catch((error) => {
      console.error("Failed to forward Stripe webhook to GAS", error);
    }),
  );

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};

export const config: Config = {
  path: "/api/stripe-webhook",
  method: ["POST"],
};
