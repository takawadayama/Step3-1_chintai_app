export default async function fetchusers() {
    const res = await fetch(process.env.API_ENDPOINT+'/user', { cache: "no-cache" });
    if (!res.ok) {
      throw new Error('Failed to fetch user');
    }
    return res.json();
  }
  