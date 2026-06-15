const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

document.getElementById('preview-btn').addEventListener('click', async () => {
    const contentElement = document.getElementById("id_content");
    const content = contentElement.value;
    const url = document.getElementById('preview-btn').dataset.url;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ content })
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('id_preview').innerHTML = data.content;
    } else if (response.status === 429) {
        location.reload()
    }
});
