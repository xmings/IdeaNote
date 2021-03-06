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

    show(content, level, timeout) {
        if (typeof level === "undefined"
            || ["success", "negative"].indexOf(level) === -1) {
            level = "success";
        }
        this.container.find(".content").html(content);
        this.container.removeClass("success").removeClass("negative").addClass(level);
        this.container.transition("fade");

        if (typeof timeout === "undefined") timeout = 3000;

        if (level === "success") {
            setTimeout(() => {
                this.container.transition('fade');
            }, timeout);
        }
    }

    hide(timeout) {
        if (typeof timeout === "undefined") {
            timeout = 0
        }

        setTimeout(() => {
            this.container.removeClass("visible");
        }, timeout);

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
            dropNoteUri: null,
            addNoteUri: null,
            syncUri: null,
            contentArea: null
        }, options);
        this.treeContainer = $(options.treeContainer);
        this.contextmenu = $(options.contextmenu);
        this.authContainer = $(options.authContainer);
        this.fetchDataUri = options.fetchDataUri;
        this.fetchContentUri = options.fetchContentUri;
        this.updateNoteUri = options.updateNoteUri;
        this.dropNoteUri = options.dropNoteUri;
        this.addNoteUri = options.addNoteUri;
        this.contentArea = options.contentArea;
        this.authUri = options.authUri;
        this.needAuthUri = options.needAuthUri;
        this.toggleNoteLockUri = options.toggleNoteLock;
        this.syncUri = options.syncUri;
        this.attribution = {
            'core': {
                'data': [],
                'force_text': true,
                'check_callback': true,
                'multiple': false,
                'themes': {
                    'dots': false,
                },
                'loaded_state': true,
                'restore_focus': false,
                'keyboard': {
                    'up': (e) => {
                        e.preventDefault();
                        let node = this.treeObj.get_node(e.target),
                            parent = this.treeObj.get_node(node.parent),
                            index = parent.children.indexOf(node.id);
                        if (index === 0) {
                            return false
                        }
                        this.treeObj.move_node(node, parent, index - 1);
                        this.treeObj.get_node(node, true).find("a").focus();
                    },
                    'down': (e) => {
                        e.preventDefault();
                        let node = this.treeObj.get_node(e.target),
                            parent = this.treeObj.get_node(node.parent),
                            index = parent.children.indexOf(node.id) + 1;
                        if (index === parent.children.length) {
                            return false
                        }
                        this.treeObj.move_node(node, parent, index + 1);
                        this.treeObj.get_node(node, true).find("a").focus();
                    },
                    'left': (e) => {
                        e.preventDefault();
                        let node = this.treeObj.get_node(e.target),
                            parent = this.treeObj.get_node(node.parent),
                            grand_parent = this.treeObj.get_node(parent.parent);
                        if (!grand_parent) {
                            return false
                        }
                        this.treeObj.move_node(node, grand_parent, grand_parent.children.length + 1);
                        this.treeObj.get_node(node, true).find("a").focus();
                    },
                    'right': (e) => {
                        e.preventDefault();
                        let node = this.treeObj.get_node(e.target),
                            prev_node = this.treeObj.get_node(this.treeObj.get_prev_dom(node, true));
                        if (!prev_node) {
                            return false
                        }
                        this.treeObj.move_node(node, prev_node, prev_node.children.length + 1);
                        this.treeObj.get_node(node, true).find("a").focus();
                    }

                }
            },
            'plugins': ['state', 'dnd', 'contextmenu', 'types'],
            'types': {
                "default": {
                    "icon": "folder icon",
                    "valid_children": ["default", "file"]
                },
                "file": {
                    "icon": "file alternate outline icon",
                    "valid_children": ["default", "file"]
                },
                "folder": {
                    "icon": "folder icon",
                    "valid_children": ["default", "file"]
                },
            },
            'contextmenu': {
                'items': {
                    'create': {
                        'label': "添加",
                        'icon': 'plus icon',
                        'separator_after': true,
                        'action': data => {
                            let parent = this.treeObj.get_node(data.reference),
                                text = "新建笔记";
                            $.ajax({
                                url: this.addNoteUri,
                                data: {
                                    title: text,
                                    pid: parent.id
                                },
                                type: 'POST',
                                dataType: 'json',
                                success: response => {
                                    this.treeObj.create_node(parent, {
                                        "id": response.id,
                                        "text": text,
                                        "type": "file"
                                    }, "last");
                                    this.treeObj.set_type(parent, "folder");
                                    this.treeObj.open_node(parent);
                                },
                                error: XMLHttpRequest => {
                                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                                }

                            });

                        }
                    },
                    'rename': {
                        'label': "重命名",
                        'icon': 'edit icon',
                        'separator_after': true,
                        'action': data => {
                            this.treeObj.edit(this.treeObj.get_node(data.reference));
                        }
                    },
                    'delete': {
                        'label': "删除",
                        'icon': 'trash icon',
                        'separator_after': true,
                        'action': data => {
                            let node = this.treeObj.get_node(data.reference),
                                parent = this.treeObj.get_node(node.parent);

                            $.ajax({
                                url: this.dropNoteUri,
                                type: "POST",
                                data: {
                                    id: node.id
                                },
                                beforeSend: XMLHttpRequest => {
                                    if (node.children.length > 0) {
                                        messageBox.show("This note has more than one child");
                                        return false
                                    }
                                    return true;
                                },
                                success: response => {
                                    if (this.treeObj.is_selected(node) && node.children.length === 0) {
                                        this.treeObj.delete_node(this.treeObj.get_selected());
                                        if (this.treeObj.get_node(parent).children.length === 0) {
                                            this.treeObj.set_icon(parent, "file alternate outline icon");
                                        }
                                    }
                                },
                                error: XMLHttpRequest => {
                                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                                }
                            });

                        }
                    },
                    'lock': {
                        'label': "锁定/解锁",
                        'icon': 'lock icon',
                        'separator_after': true,
                        'action': data => {
                            let node = this.treeObj.get_node(data.reference);
                            $.ajax({
                                url: this.toggleNoteLockUri,
                                data: {id: node.id},
                                type: "POST",
                                error: (XMLHttpRequest) => {
                                    if (XMLHttpRequest.status === 401) {
                                        messageBox.show("该目录已加密，请先解锁再去锁！", "success", 3000)
                                    } else {
                                        messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText);
                                    }
                                }
                            })
                        }
                    },
                    'sync': {
                        'label': "同步该笔记",
                        'icon': 'sync icon',
                        'separator_after': true,
                        'action': data => {
                            let node = this.treeObj.get_node(data.reference);
                            $.ajax({
                                url: this.syncUri,
                                data: {
                                    id: node.id,
                                    with_children: 0
                                },
                                type: 'POST',
                                success: e => {
                                    messageBox.show("笔记《" + node.text + "》同步成功.")
                                },
                                error: XMLHttpRequest => {
                                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                                }

                            });

                        }
                    },
                    'sync_with_children': {
                        'label': "同步笔记树",
                        'icon': 'sync icon',
                        'separator_after': true,
                        'action': data => {
                            let node = this.treeObj.get_node(data.reference);
                            $.ajax({
                                url: this.syncUri,
                                data: {
                                    id: node.id,
                                    with_children: 1
                                },
                                type: 'POST',
                                success: e => {
                                    messageBox.show("笔记《" + node.text + "》及其子笔记同步成功.")
                                },
                                error: XMLHttpRequest => {
                                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                                }

                            });

                        }
                    },
                }
            }
        };

        this.treeContainer.on("select_node.jstree", (e, data) => {
            $.ajax({
                url: this.fetchContentUri,
                data: {
                    id: data.node.id
                },
                success: content => {
                    let item = localStorage.getItem("ideanote-" + data.node.id);
                    if (typeof item === "string") {
                        content = JSON.parse(item).content;
                    }
                    this.contentArea.switchDoc(data.node.id, content);
                },
                error: XMLHttpRequest => {
                    messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText);
                }
            });
            this.contentArea.editorObj.execCommand("goDocEnd");
            this.contentArea.editorObj.focus();
        });

        this.treeContainer.on("rename_node.jstree", (e, data) => {
            $.ajax({
                url: this.updateNoteUri,
                type: 'POST',
                data: {
                    title: data.node.text,
                    type: "rename",
                    id: data.node.id
                },
                error: function (XMLHttpRequest) {
                    messageBox.show("修改结点名称失败: "
                        + XMLHttpRequest.responseText, "negative");
                }
            });
        });

        this.treeContainer.on('move_node.jstree', (e, data) => {
            $.ajax({
                url: this.updateNoteUri,
                type: 'POST',
                data: {
                    parent_id: data.parent,
                    index: data.position,
                    id: data.node.id,
                    type: "position"
                },
                success: () => {
                    this.treeObj.open_node(this.treeObj.get_node(data.parent));
                },
                error: (XMLHttpRequest) => {
                    messageBox.show("修改结点名称失败: "
                        + XMLHttpRequest.responseText, "negative");
                }
            })
        });

        this.treeContainer.on("before_open.jstree", (e, data) => {
            if (data.node.type === "folder") {
                $.get(this.needAuthUri, {id: data.node.id}, (res) => {
                    if (res.status) {
                        this.treeObj.close_node(data.node.id);
                        this.treeObj.select_node(data.node.id);
                        this.authContainer.find("input").attr("data-note-id", data.node.id);
                        this.authContainer.css("visibility", "visible");
                        this.authContainer.find("input").focus();
                    }
                })
            }
        });

        this.authContainer.find(".button").click(() => {
            let input = this.authContainer.find("input");
            $.ajax({
                url: this.authUri,
                type: "POST",
                data: {
                    id: input.attr("data-note-id"),
                    auth_code: input.val()
                },
                beforeSend: () => {
                    this.authContainer.css("visibility", "hidden");
                },
                success: () => {
                    let id = this.authContainer.find("input").attr("data-note-id");
                    this.treeObj.open_node(this.treeObj.get_node(id));
                    this.treeObj.select_node(this.treeObj.get_selected()[0]);
                },
                error: () => {
                    messageBox.show("Hi dude, please enter the correct password", "negative");
                    messageBox.hide(2000)
                }
            });
        });

        $(document).on('click', (e) => {
            if ($(e.target) !== this.authContainer
                && this.authContainer.has($(e.target)).length === 0) {
                this.authContainer.css("visibility", "hidden");
            }

            if ($(e.target) !== messageBox.container
                && messageBox.container.has($(e.target)).length === 0) {
                messageBox.hide();
            }
        });

        $(document).on("keydown", (e) => {
            if (this.authContainer.css("visibility") === "visible") {
                if (e.keyCode === 13) {
                    e.preventDefault();
                    this.authContainer.find(".button").click();
                }
            }
        })
    }

    buildTree() {
        $.ajax({
            url: this.fetchDataUri,
            type: "GET",
            dataType: "json",
            success: data => {
                this.attribution.core.data = data;
                this.treeContainer.jstree(this.attribution);
                this.treeObj = this.treeContainer.jstree(true);
            },
            error: XMLHttpRequest => {
                messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative")
            }
        });

    }

}

class ContentArea {
    constructor(options) {
        options = Object.assign({
            editContainer: "#editor",
            viewContainer: "#preview",
            outlineContainer: "#toc",
            toolClassName: null,
            submitContentUri: null,
            submitImageUri: null
        }, options);

        this.editContainer = $(options.editContainer).get(0);
        this.viewContainer = $(options.viewContainer);
        this.outlineContainer = $(options.outlineContainer);
        this.toolClassName = $(options.toolClassName);
        this.submitContentUri = options.submitContentUri;
        this.submitImageUri = options.submitImageUri;
        this.toolPageUri = options.toolPageUri;
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

            localStorage.setItem("ideanote-" + this.currentNoteId, JSON.stringify({
                "id": this.currentNoteId,
                "content": content,
                "changeTime": (new Date()).toISOString()
            }));
        });

        setInterval(() => this.saveChangedNote(), 5000);

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

        this.editorObj.on("blur", (instance, event)=>{
            this.saveChangedNote();
            console.log("go");
        });

        this.toolClassName.click(e => {
            $.ajax({
                url: this.toolPageUri,
                data: {"type": $(e.target).attr("data-tool-type")},
                dataType: "html",
                success: e => {
                    this.viewContainer.html(e);
                }
            })
        });

    }

    saveChangedNote() {
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            if (key.startsWith("ideanote")) {
                let text = localStorage.getItem(key);
                let note = JSON.parse(text);
                $.ajax({
                    url: this.submitContentUri,
                    type: "POST",
                    data: {
                        id: note.id,
                        type: "content",
                        content: note.content,
                    },
                    success: () => {
                        if (text === localStorage.getItem(key)) localStorage.removeItem(key);
                    },
                    error: XMLHttpRequest => {
                        messageBox.show(XMLHttpRequest.responseText || XMLHttpRequest.statusText, "negative");
                    }
                });
            }
        }


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
        if (content.startsWith("<!--html-->")) {
            this.viewContainer.html(content);
            return
        }

        this.viewContainer.html(
            marked(content, {
                highlight: function (code, language) {
                    if (typeof (language) === "undefined") return code;
                    if (["java", "python", "bash", "shell", "c", "sql", "js"].indexOf(language.toLowerCase()) < 0) return code;
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

export {Catalog, ContentArea, messageBox};