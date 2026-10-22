const TOKEN_KEY = "careeros_token";
let memoryToken: string | null = null;

export function saveToken(token: string) {
  if (typeof window !== "undefined") {
    memoryToken = token;
    const secure = window.location.protocol === "https:" ? "; secure" : "";
    document.cookie = `${TOKEN_KEY}=${encodeURIComponent(token)}; path=/; max-age=86400; samesite=lax${secure}`;
  }
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  if (memoryToken) return memoryToken;
  const match = document.cookie.match(new RegExp(`${TOKEN_KEY}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function clearToken() {
  if (typeof window !== "undefined") {
    document.cookie = `${TOKEN_KEY}=; path=/; max-age=0; samesite=lax`;
    memoryToken = null;
  }
}
