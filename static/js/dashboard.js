/* global d3, rana */

function setupApiKeyCopy() {
  if (typeof navigator.clipboard === 'undefined') {
    // no clipboard support :/
    console.warn('no navigator.clipboard support')
    return
  }

  const targets = document.getElementsByClassName('api-key')
  for (const target of targets) {
    target.addEventListener('click', () => {
      navigator.clipboard.writeText(target.innerText).then(
        () => {
          const paragraph = target.parentNode.parentNode
          const smalls = paragraph.getElementsByTagName('small')
          if (smalls.length === 0) {
            return
          }
          const small = smalls[0]
          const original = small.innerText

          small.style.animation = 'flash-mark ease 1s'
          small.innerText = '(copied!)'
          setTimeout(() => {
            small.innerText = original
            small.style.animation = 'inherit'
          }, 1000)
        },
        () => {
          window.alert('failed to copy api key to clipboard 😔')
        }
      )
    })
  }
}

async function loadGraph() {
  await rana.request('/api/v1/users/current/summaries')
}

document.addEventListener('DOMContentLoaded', () => {
  setupApiKeyCopy()
  loadGraph()
})

// d3.select('body')
//   .append('div')
//   .html('<h2>uwu</h2>')
