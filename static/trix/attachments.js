(function() {
    const PATH = "/files/upload";

    addEventListener("trix-attachment-add", function(event) {
        if (event.attachment.file) {
            uploadFileAttachment(event.attachment)
        }
    });

    function uploadFileAttachment(attachment) {
        uploadFile(attachment.file, setProgress, setAttributes)

        function setProgress(progress) {
            attachment.setUploadProgress(progress)
        }

        function setAttributes(attributes) {
            attachment.setAttributes(attributes)
        }
    }

    function uploadFile(file, progressCallback, successCallback) {
        const formData = createFormData(file);
        const xhr = new XMLHttpRequest();

        xhr.open("POST", PATH, true);

        xhr.upload.addEventListener("progress", function(event) {
            const progress = event.loaded / event.total * 100;
            progressCallback(progress)
        });

        xhr.addEventListener("load", function(event) {
            if (xhr.status === 201) {
                debugger;
                const attributes = {
                    url: xhr.getResponseHeader("Location"),
                    href: xhr.getResponseHeader("Location") + "?content-disposition=attachment"
                };
                successCallback(attributes)
            }
        });

        xhr.send(formData)
    }

    // function createStorageKey(file) {
    //   var date = new Date();
    //   var day = date.toISOString().slice(0,10);
    //   var name = date.getTime() + "-" + file.name;
    //   return [ "tmp", day, name ].join("/");
    // }

    function createFormData(file) {
        const data = new FormData();
        data.append("Content-Type", file.type);
        data.append("file", file);
        return data
    }
})();