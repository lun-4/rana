/* global dateFns */

const RANA_ENDPOINT = `${location.protocol}//${location.host}`

function formatDate(date) {
  return dateFns.format(date, 'YYYY-MM-DD')
}

class RanaClient {
  constructor(key, { endpoint = RANA_ENDPOINT } = {}) {
    this.endpoint = endpoint
    this.key = key
  }

  keyAsBase64() {
    return window.btoa(this.key)
  }

  summaries(daysBack) {
    const start = formatDate(dateFns.subDays(new Date(), daysBack))
    const end = formatDate(new Date())
    return this.request('/api/v1/users/current/summaries', { start, end })
  }

  async request(path, query = {}) {
    const queryParams =
      Object.keys(query).length !== 0
        ? '?' +
          Object.entries(query)
            .map(([key, value]) => `${key}=${value}`)
            .join('&')
        : ''

    const resp = await fetch(this.endpoint + path + queryParams, {
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
