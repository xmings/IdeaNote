class MessageBox {
    constructor(options) {
        options = Object.assign({
            container: "#flash-message"
        }, options);

        this.container = $(options.container);
        this.container.find(".close").click(() => {
            this.container.transition('fade');
        });
    }

    show(content, level) {
        if (typeof level === "undefined"
            || ["success", "negative"].indexOf(level) === -1) {
            level = "success";
        }
        this.container.find(".content").html(content);
        this.container.removeClass("success").removeClass("negative").addClass(level);
        this.container.transition("fade");

        if (level === "success") {
            setTimeout(() => {
                this.container.transition('fade');
            }, 2000);
        }
    }
}

let messageBox = new MessageBox();

class Catalog {
    constructor(options) {
        options = Object.assign({
            treeContainer: "#tree",
            contextmenu: "#contextmenu",
            fetchDataUri: null,
            fetchContentUri: null,
            updateNoteUri: null,
            syncUri: null,
            dropNoteUri: null,
            addNoteUri: null,
            contentArea: null
        }, options);
        this.treeContainer = $(options.treeContainer);
        this.contextmenu = $(options.contextmenu);
        this.fetchDataUri = options.fetchDataUri;
        this.fetchContentUri = options.fetchContentUri;
        this.updateNoteUri = options.updateNoteUri;
        this.dropNoteUri = options.dropNoteUri;
        this.addNoteUri = options.addNoteUri;
        this.syncUri = options.syncUri;
        this.contentArea = options.contentArea;
        this.selectedNode = null;
        this.changeSequenceMode = false;
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
                onClick: (event, treeId, treeNode) => {
                    this.selectedNode = treeNode;
                    this.fetchNote();
                    this.contentArea.editorObj.execCommand("goDocEnd");
                    this.contentArea.editorObj.focus();
                },
                onRename: (event, treeId, treeNode) => {
                    this.selectedNode = treeNode;
                    this.rename();
                    this.treeContainer.find("#" + treeNode.tId + ">a").click();

                },
                onRightClick: (event, treeId, treeNode) => {
                    if (treeNode) {
                        this.treeContainer.find("#" + treeNode.tId + ">a").click();
                        let y = event.originalEvent.y;
                        if (y + this.contextmenu.height() >= window.innerHeight) {
                            y = $(document).innerHeight() - this.contextmenu.height() - 10;
                        }
                        this.contextmenu.css({
                            "left": event.originalEvent.x,
                            "top": y
                        }).show();
                    } else {
                        this.contextmenu.hide();
                    }
                },
                onDrop: (event, treeId, treeNodes, targetNode, moveType, isCopy) => {
                    let direction = moveType === "inner" ? "down-level" : "down-index";
                    console.log(treeId);
                    console.log(treeNodes);
                    console.log(targetNode);
                    if (!isCopy && targetNode && treeNodes[0].pId) {
                        $.ajax({
                            url: this.updateNoteUri,
                            type: 'POST',
                            data: {
                                type: direction,
                                target_note_id: targetNode.id,
                                id: treeNodes[0].id
                            },
                            error: function (XMLHttpRequest) {
                                messageBox.show("修改结点名称失败: "
                                    + XMLHttpRequest.responseText, "negative");
                            }
                        })
                    }
                }
            }
        };

        this.contextmenu.find(".add-note").click(() => {
            this.addNote();
        });

        this.contextmenu.find(".drop-note").click(() => {
            this.dropNote();
        });

        this.contextmenu.find(".rename").click(() => {
            this.treeObj.editName(this.selectedNode);
        });

        this.contextmenu.find(".sync").click(() => {
            this.sync()
        });

        $(document).click(e => {
            this.changeSequenceMode = $(e.target).hasClass("node_name");
            this.contextmenu.hide();
        });

        $(document).contextmenu(e => {
            this.contextmenu.hide();
        });
        $(document).keydown(event => {
            if (event.ctrlKey && event.keyCode === 83) {
                // ctrl+s pull&&push
                this.sync();
                event.preventDefault();
            } else if (this.changeSequenceMode === true) {
                    if (event.keyCode === 38) {
                        this.move_by_arrow("up-index");
                    } else if (event.keyCode === 40) {
                        this.move_by_arrow("down-index");
                    } else if (event.keyCode === 37) {
                        this.move_by_arrow("up-level");
                    } else if (event.keyCode === 39) {
                        this.move_by_arrow("down-level");
                    }
            }else{
                this.changeSequenceMode = false;
            }

        })

    }

    buildTree() {
        $.ajax({
            url: this.fetchDataUri,
            type: "GET",
            dataType: "json",
            success: data => {
                this.treeObj = $.fn.zTree.init(this.treeContainer, this.attribution, data);
                this.root = this.treeObj.getNodes()[0];
                this.treeContainer.find("#" + this.root.tId + ">a").click();
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative")
            }
        });

    }

    fetchNote() {
        $.ajax({
            url: this.fetchContentUri,
            data: {
                id: this.selectedNode.id
            },
            success: content => {
                this.contentArea.switchDoc(this.selectedNode.id, content);
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
            }
        })
    }

    addNote() {
        let newNodes = this.treeObj.addNodes(this.selectedNode, -1, {name: "新建节点"}),
            newNode = this.treeObj.getNodeByTId(newNodes[0].tId);
        $.ajax({
            url: this.addNoteUri,
            data: {
                title: "新建节点",
                pid: this.selectedNode.id
            },
            type: 'POST',
            dataType: 'json',
            success: response => {
                newNode.id = response.id;
                this.treeObj.updateNode(newNode);
                this.treeObj.editName(newNode);
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
            }

        })
    }

    dropNote() {
        $.ajax({
            url: this.dropNoteUri,
            type: "POST",
            data: {
                id: this.selectedNode.id
            },
            success: response => {
                this.treeObj.removeNode(this.selectedNode);
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
            }
        })
    }

    rename() {
        $.ajax({
            url: this.updateNoteUri,
            type: 'POST',
            data: {
                title: this.selectedNode.name,
                type: "rename",
                id: this.selectedNode.id
            },
            error: function (XMLHttpRequest) {
                messageBox.show("修改结点名称失败: "
                    + XMLHttpRequest.responseText, "negative");
            }
        })
    }

    move_by_arrow(direction) {
        let targetNode = null;

        if (direction === "up-index") {
            targetNode = this.selectedNode.getPreNode();
        } else if (direction === "down-index") {
            targetNode = this.selectedNode.getNextNode();
        } else if (direction === "up-level") {
            let parent = this.selectedNode.getParentNode();
            if (parent.level === 0) {
                messageBox.show("该笔记父目录已是根目录，不能上移");
                return;
            }
            targetNode = parent;
        } else {
            targetNode = this.selectedNode.getPreNode();
        }
        if (!targetNode) return;

        $.ajax({
            url: this.updateNoteUri,
            type: 'POST',
            data: {
                type: direction,
                target_note_id: targetNode.id,
                id: this.selectedNode.id
            },
            error: function (XMLHttpRequest) {
                messageBox.show("修改结点名称失败: "
                    + XMLHttpRequest.responseText, "negative");
            },
            success: () => {
                if (direction === "up-index") {
                    this.treeObj.moveNode(targetNode, this.selectedNode, "prev");
                } else if (direction === "down-index") {
                    this.treeObj.moveNode(targetNode, this.selectedNode, "next");
                } else if (direction === "up-level") {
                    this.treeObj.moveNode(targetNode, this.selectedNode, "next");
                } else if (direction === "down-level") {
                    this.treeObj.moveNode(targetNode, this.selectedNode, "inner");
                }
                this.treeObj.updateNode(this.selectedNode);
            }
        })

    }

    sync() {
        messageBox.show("<i class='notched circle loading icon'></i>同步中 ...");
        $.ajax({
            url: this.syncUri,
            type: 'POST',
            success: () => {
                messageBox.show("同步成功");
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
            }
        })
    }

}

class ContentArea {
    constructor(options) {
        options = Object.assign({
            editContainer: "#editor",
            viewContainer: "#preview",
            outlineContainer: "#toc",
            submitContentUri: null,
            submitImageUri: null
        }, options);

        this.editContainer = $(options.editContainer).get(0);
        this.viewContainer = $(options.viewContainer);
        this.outlineContainer = $(options.outlineContainer);
        this.submitContentUri = options.submitContentUri;
        this.submitImageUri = options.submitImageUri;
        this.currentNoteId = null;
        this.splitter1 = null;
        this.splitter2 = null;
        this.attribution = {
            mode: 'markdown',
            theme: 'idea monokai',
            extraKeys: {"Ctrl": "autocomplete"},//ctrl可以弹出选择项
            lineNumbers: true,//显示行号
            autoCloseTags: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            showCursorWhenSelecting: true,
            autofocus: true,
            lineWrapping: true,
            value: "写你想写",
            tabSize: 4,
            indentUnit: 4,
            smartIndent: true,
            spellcheck: false,
            lineSeparator: "",
            scrollbarStyle: null
        };
        this.docBuffer = {};
        this.editorObj = CodeMirror.fromTextArea(this.editContainer, this.attribution);
        this.toc = new Toc();

        this.editorObj.on("changes", (instance, changes) => {
            let content = this.editorObj.doc.getValue();
            this.previewContent(content);
            this.toc.build();

            $.ajax({
                url: this.submitContentUri,
                type: "POST",
                data: {
                    id: this.currentNoteId,
                    type: "content",
                    content: content,
                },
                error: XMLHttpRequest => {
                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                }
            });

        });

        this.editorObj.on('scroll', e => {
            let scrollRate = this.editorObj.getScrollInfo().top / this.editorObj.getScrollInfo().height;
            this.viewContainer[0].scrollTop = (this.viewContainer[0].scrollHeight) * scrollRate;
        });

        this.editorObj.on('paste', (editor, e) => {
            if (typeof e.clipboardData === "object") {
                let items = e.clipboardData.items || e.clipboardData.files || [];

                $.each(items, (index, item) => {
                    if (item.kind === "file" && item.type.match(/^image/).length > 0) {
                        let formData = new FormData(),
                            image = item.getAsFile();
                        if (image === null) {
                            messageBox.show("剪切板中不存在图片");
                            return
                        }
                        formData.append('image', item.getAsFile());
                        formData.append('id', this.currentNoteId);

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
                            error: XMLHttpRequest => {
                                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                            }
                        })
                    }
                });
            }

        });

    }

    initWindowSplit(firstContainer, secondContainer) {
        let eheight = window.innerHeight;
        this.splitter1 = $(firstContainer).height(eheight).split({
            orientation: 'vertical',
            limit: 10,
            percent: true,
            position: '15%',
            width: 1,
            invisible: false,
            onDrag: () => {
                if (this.splitter1.position() < 100) {
                    this.splitter1.position(0)
                }
            }
        });

        this.splitter2 = $(secondContainer).height(eheight).split({
            orientation: 'vertical',
            limit: 0,
            percent: true,
            position: '0%',
            width: 1,
            invisible: false,
            onDrag: () => {
                if (this.splitter2.position() < 200) {
                    this.splitter2.position(0)
                }
            }
        });

        // 快捷键
        $(document).keydown(event => {
            if (event.keyCode === 27) {
                // esc 返回只读模式
                this.splitter2.position("0%");
                event.preventDefault();
            } else if (event.ctrlKey && event.keyCode === 73) {
                // ctrl+i 进入编辑模式
                this.splitter2.position("50%");
                this.editorObj.refresh();
                event.preventDefault();
            } else if (event.shiftKey && event.keyCode === 83) {
                // shift+s 切换侧边栏(目录树)
                if (this.splitter1.position() > 15) {
                    this.splitter1.position("0%")
                } else {
                    this.splitter1.position("15%");
                }
                event.preventDefault();
            } else if (event.ctrlKey && event.shiftKey && event.keyCode === 70) {
                // ctrl+shift+f //全屏编辑+预览
                this.splitter1.position("0%");
                this.splitter2.position("60%");
                event.preventDefault();
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

    switchDoc(id, content) {
        if (id in this.docBuffer) {
            this.editorObj.swapDoc(this.docBuffer[id]);
        } else {
            this.docBuffer[id] = CodeMirror.Doc(content, "markdown");
            this.editorObj.swapDoc(this.docBuffer[id]);
        }
        this.currentNoteId = id;
        this.previewContent(content);
        this.toc.build();
    }
}

class Toc {
    constructor(options) {
        options = Object.assign({
            tocContainer: '#toc',
            contentContainer: '#preview',
            heading: 'h1,h2,h3,h4,h5,h6,h7'
        }, options);
        this.tocContainer = $(options.tocContainer);
        this.contentContainer = $(options.contentContainer);
        this.heading = options.heading.toUpperCase();
        this.headingList = this.heading.split(",");
    }

    build() {
        let lastLevel = -1,
            tocHtmlString = "",
            id = 1000;
        this.contentContainer.find(this.heading).each((index, ele) => {
            let level = this.headingList.indexOf(ele.tagName);
            if (lastLevel >= 0) {
                for (let i = 0; i < Math.abs(lastLevel - level); i++) {
                    if (lastLevel < level) {
                        tocHtmlString = tocHtmlString.replace(/<\/li>$/, "");
                        tocHtmlString += "<ol class='list-unstyled'>"
                    } else if (lastLevel > level) {
                        tocHtmlString += "</li></ol>"
                    }
                }
            }

            $(ele).attr("id", id);
            tocHtmlString += "<li><a href='#" + id + "'>" + $(ele).text() + "</a></li>";
            lastLevel = level;
            id += 1;
        });

        this.tocContainer.html(tocHtmlString);
    }

}

export {Catalog, ContentArea};