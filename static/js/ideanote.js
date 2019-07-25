export function flashMessage(content, level) {
    let flash = $(".flash-message");
    flash.find(".content").html(content);
    if (typeof level === "undefined" || ["success", "negative"].indexOf(level) === -1) level = "success";
    flash.removeClass("success").removeClass("negative").addClass(level);
    flash.addClass("visible");
    if (level === "success") {
        setTimeout(function () {
            flash.transition('fade');
        }, 2000);
    }
}

export class Catalog {
    constructor(container, contextmenu, fetchDataUri,
                fetchContentUri, updateNoteUri, dropNoteUri, editorObj) {
        this.container = $(container);
        this.contextmenu = $(contextmenu);
        this.fetchDataUri = fetchDataUri;
        this.fetchContentUri = fetchContentUri;
        this.updateNoteUri = updateNoteUri;
        this.dropNoteUri = dropNoteUri;
        this.editorObj = editorObj;
        this.selectedItem = null;
        this.attribution = {
            check: {
                enable: false
            },
            data: {
                simpleData: {
                    enable: true
                }
            },
            edit: {
                drag: {
                    isCopy: false,
                    isMove: true,
                },
                enable: true,
                showRemoveBtn: false,
                showRenameBtn: false
            },
            view: {
                selectedMulti: false
            },
            callback: {
                onClick: (event, treeId, node) => {
                    $.ajax({
                        url: this.fetchContentUri,
                        data: {
                            id: node.id
                        },
                        success: content => {
                            this.editorObj.doc.clearHistory();
                            this.editorObj.firstOpen = true;
                            this.editorObj.setValue(content);
                        }
                    })
                },
                onRename: (event, treeId, treeNode) => {
                    $.ajax({
                        url: this.updateNoteUri,
                        type: 'POST',
                        data: {
                            title: treeNode.name,
                            id: treeNode.id
                        },
                        error: function (XMLHttpRequest) {
                            flashMessage("修改结点名称失败: "
                                + XMLHttpRequest.responseText, "negative");
                        }
                    })
                },
                beforeRightClick: (treeId, treeNode) => {
                    this.treeObj.selectNode(treeNode);
                },
                onDrop: function (event, treeId, treeNodes, targetNode, moveType, isCopy) {
                    if (targetNode !== null && isCopy === false) {
                        if (moveType === 'inner') {
                            $.ajax({
                                url: this.dropNoteUri,
                                type: 'POST',
                                data: {
                                    id: treeNodes[0].id,
                                    pid: targetNode.id
                                },
                                success: function () {

                                },
                                error: function () {

                                }

                            })
                        }
                    }
                }
            }
        };
    }

    #initContextmenu() {
        this.container.find("a[class^='level']").contextmenu(e => {
            console.log("oij");
            this.contextmenu.css({"left": e.x, "top": e.y}).show();
            e.preventDefault();
        });

        $(document).click(e => {
            this.contextmenu.hide();
        });

        $(document).contextmenu(e => {
            this.contextmenu.hide();
        });
    }

    buildTree() {
        $.ajax({
            url: this.fetchDataUri,
            type: "GET",
            dataType: "json",
            success: data => {
                this.treeObj = $.fn.zTree.init(this.container, this.attribution, data);
                this.root = this.treeObj.getNodes()[0];
                this.treeObj.selectNode(this.root);
                this.container.find(".curSelectedNode").click();
                this.initContextmenu();
            },
            error: XMLHttpRequest => {
                flashMessage(XMLHttpRequest.responseText, "negative")
            }
        });

    }


}

export class ContentArea {
    constructor(editContainer, viewContainer, outlineContainer, submitContentUri, submitImageUri) {
        this.editContainer = $(editContainer);
        this.viewContainer = $(viewContainer);
        this.outlineContainer = $(outlineContainer);
        this.submitContentUri = submitContentUri;
        this.submitImageUri = submitImageUri;
        this.currentNoteId = null;
        this.attribution = {
            theme: 'idea monokai',
            extraKeys: {"Ctrl": "autocomplete"},//ctrl可以弹出选择项
            lineNumbers: true,//显示行号
            autoCloseTags: true,
            autofocus: true,
            value: "写你想写",
            matchBrackets: true,
            tabSize: 4,
            indentUnit: 4,
            smartIndent: true,
            spellcheck: false,
            lineSeparator: "",
            scrollbarStyle: null
        };
        this.editorObj = CodeMirror.fromTextArea(this.editContainer, this.attribution);
        this.firstOpen = true;

        this.editorObj.on("changes", e => {
            let content = this.editorObj.getValue();
            this.previewContent(content);
            this.freshOutline();

            if (this.firstOpen === true) {
                this.firstOpen = false;
                return
            }

            $.ajax({
                url: this.submitContentUri,
                type: "POST",
                data: {
                    id: this.currentNoteId,
                    content: content,
                },
                error: function () {
                    flashMessage("保存失败", "negative");
                }
            });

        });


        this.editorObj.on('scroll', e => {
            let scrollRate = this.editorObj.getScrollInfo().top / this.editorObj.getScrollInfo().height;
            this.viewContainer[0].scrollTop = (this.viewContainer[0].scrollHeight) * scrollRate;
        });

        this.editorObj.on('paste', function (editor, e) {
            if (typeof e.clipboardData === "object") {
                let items = e.clipboardData.items || e.clipboardData.files || [];

                $.each(items, function (index, item) {
                    if (item.kind === "file" && item.type.match(/^image/).length > 0) {
                        let formData = new FormData(),
                            image = item.getAsFile();
                        if (image === null) {
                            flashMessage("剪切板中不存在图片");
                            return
                        }
                        formData.append('image', item.getAsFile());
                        formData.append('id', zTreeObj.getSelectedNodes()[0].id);

                        $.ajax({
                            url: this.submitImageUri,
                            type: 'POST',
                            cache: false,
                            data: formData,
                            processData: false,
                            contentType: false,
                            dataType: 'json',
                            success: result => {
                                let mdUrl = "![image](url)".replace("url", result['filename']);
                                this.editorObj.replaceSelection(mdUrl)
                            },
                            error: function () {
                                flashMessage("图片保存失败", true)
                            }
                        })
                    }
                });
            }

        });


    }


    previewContent(content) {
        //content = content.replace(/\n\n/g, "\n<br>");
        this.viewContainer.html(
            marked(content, {
                highlight: function (code) {
                    return hljs.highlightAuto(code).value;
                },
                pedantic: false,
                gfm: true,
                tables: true,
                breaks: true,
                sanitize: false,
                smartLists: true,
                smartypants: false,
                xhtml: false,
                headerIds: true,
                langPrefix: 'hljs ',
                //baseUrl: 'http://localhost:5555/'
            })
        );

    }

    freshOutline() {
        this.outlineContainer.toc({
                content: ".preview",
                headings: "h1,h2,h3,h4"
            }
        );
    }
}
