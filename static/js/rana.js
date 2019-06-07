const RANA_ENDPOINT = `${location.protocol}//${location.host}`

class RanaClient {
  constructor(key, { endpoint = RANA_ENDPOINT } = {}) {
    this.endpoint = endpoint
    this.key = key
  }

  keyAsBase64() {
    return window.btoa(this.key)
  }

  async request(path) {
    const resp = await fetch(this.endpoint + path, {
      headers: {
        Authorization: `Basic ${this.keyAsBase64()}`,
      },
    })

    if (!resp.ok) {
      let message = `HTTP ${resp.status}`

      try {
        const payload = await resp.json()
        if (payload.error) {
          message += ` (${payload.error})`
        }
      } catch (_error) {
        message += ' (No error field.)'
      }

      throw new Error(message)
    }

    console.log(await resp.json())
  }
}
