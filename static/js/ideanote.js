(function ($) {

    $.fn.catalog = function (options) {
        let settings = $.extend({
            treeDataUrl: '',
            flashFunc: $.noop,
            nodeContent: '',
            previewFunc: $.noop,
            editor: ''
        }, options || {});

        treeAttr = {
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
                onClick: function (event, treeId, node) {
                    $.get(
                        url = settings.nodeContent,
                        data = {
                            id: node.id
                        },
                        success = function (content) {
                            settings.editor.doc.clearHistory();
                            settings.editor.__proto__.reinit = true;
                            settings.editor.setValue(content);
                            settings.previewFunc(content);
                        }
                    )
                },
                onRename: function (event, treeId, treeNode) {
                    $.ajax({
                        url: settings.renameUrl,
                        type: 'POST',
                        data: {
                            title: treeNode.name,
                            id: treeNode.id
                        },
                        error: function (XMLHttpRequest) {
                            settings.flashFunc("修改结点名称失败: " + XMLHttpRequest.toString() , true);
                        }
                    })
                },
                beforeRightClick: function (treeId, treeNode) {
                    zTreeObj.selectNode(treeNode);
                },
                onDrop: function (event, treeId, treeNodes, targetNode, moveType, isCopy) {
                    if (targetNode !== null && isCopy === false) {
                        if (moveType === 'inner') {
                            $.ajax({
                                url: "{{ url_for('core.update_note', type='position') }}",
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

        treeRoot = this;
        $.ajax({
            url: settings.treeDataUrl,
            type: 'GET',
            dataType: 'json',
            success: function (jNodes) {
                zTreeObj = $.fn.zTree.init(treeRoot, treeAttr, jNodes);
                node = zTreeObj.getNodes()[0];
                zTreeObj.selectNode(node);
                $.zTreeObj = zTreeObj;
                treeRoot.find(".curSelectedNode").click();
            },

        });

    };

    $.bindTreePopu = function (options) {
        let settings = $.extend({
            nodeSeletor: '',
            dropUrl: '',
            renameUrl: '',
            addChildUrl: '',
            flashFunc: $.noop,
        }, options || {});

        $.syncNote = function () {
            $.ajax({
                url: settings.syncUrl,
                type: 'POST',
                beforeSend: function () {
                    settings.flashFunc("同步中 ... <i class='icon-spinner icon-spin'></i>")
                },
                success: function () {
                    settings.flashFunc("同步成功", true);
                },
                error: function () {
                    settings.flashFunc("同步失败, 请手工同步");
                }
            })
        };

        $.contextMenu({
            selector: settings.nodeSeletor,
            trigger: 'right',
            className: 'contextmenu-item-custom',
            callback: function (key, options) {
                test = options;
                nodeId = options.$trigger[0].parentNode.id;
                node = zTreeObj.getNodeByTId(nodeId);
                if (key === 'drop') {
                    $.post(url = settings.dropUrl,
                        data = {
                            id: node.id
                        },
                        success = function (response) {
                            zTreeObj.removeNode(node);
                        }
                    )

                } else if (key === 'addChild') {
                    newNodes = zTreeObj.addNodes(node, -1, {name: "新建节点"});
                    newNode = zTreeObj.getNodeByTId(newNodes[0].tId);

                    $.ajax({
                        url: settings.addChildUrl,
                        data: {
                            title: "新建节点",
                            pid: node.id
                        },
                        type: 'POST',
                        dataType: 'json',
                        success: function (response) {
                            newNode.id = response.id;
                            zTreeObj.updateNode(newNode)
                        },
                        error: function (err) {
                            settings.flashFunc(err);
                        }

                    })

                } else if (key === 'rename') {
                    zTreeObj.editName(node);

                } else if (key === 'sync') {
                    $.syncNote();
                }
            },
            items: {
                "addChild": {
                    name: "添加子节点", icon: function () {
                        return ' icon-plus-sign-alt context-menu-awesome'
                    }
                },
                "sep1": "---------",
                "rename": {
                    name: "重命名", icon: function () {
                        return 'icon-edit context-menu-awesome';
                    }
                },
                "drop": {
                    name: "删除", icon: function () {
                        return 'icon-trash context-menu-awesome'
                    }
                },
                "sync": {
                    name: "同步", icon: function () {
                        return 'icon-refresh context-menu-awesome';
                    }
                }
            }
        });
    };

    $.fn.toc = function (options) {
        let settings = $.extend({
            content: 'body',
            heading: 'h1,h2,h3,h4,h5,h6,h7'
        }, options || {});

        lastLevel = -1;
        tocHtmlString = "";
        id = 1000;
        settings.heading = settings.heading.toUpperCase();
        headingList = settings.heading.split(",");
        $(settings.content).find(settings.heading).each(function () {
            level = headingList.indexOf(this.tagName);

            if (lastLevel >= 0) {
                for (let i = 0; i < Math.abs(lastLevel - level); i++) {
                    if (lastLevel < level) {
                        tocHtmlString = tocHtmlString.replace(/<\/li>$/,"");
                        tocHtmlString += "<ul class='list-unstyled'>"
                    } else if (lastLevel > level) {
                        tocHtmlString += "</li></ul>"
                    } else {
                        tocHtmlString += "</li>"
                    }
                }
            }

            $(this).attr("id", id);
            tocHtmlString += "<li><a href='#" + id + "'>" + $(this).text() + "</a></li>";

            lastLevel = level;
            id += 1;
        });

        $(this).html(tocHtmlString);
    };
})(jQuery);