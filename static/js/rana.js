const RANA_URL = "https://rana.discordapp.io/api/v1";

class RanaClient {
    constructor (apiKey) {
        this.apiKey = apiKey;
    }

    doRequest(path) {
        let b64_api_key = window.btoa(this.apiKey);

        fetch(`${rana_url}${path}`, {
            headers: {
                'Authorization': `Basic ${b64_api_key}`,
            }
        }).then(function(response) {
            return response.json();
        })
    }
}

