(function ($) {

    $.fn.catalog = function (options) {
        var settings = $.extend({
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
                            nodeId: node.id
                        },
                        success = function (content) {
                            settings.editor.val(content);
                            settings.previewFunc(content);
                        }
                    )
                },
                onRename: function(event, treeId, treeNode) {
                    $.ajax({
                        url: settings.renameUrl,
                        type: 'POST',
                        data: {
                            nodeTitle: treeNode.name,
                            nodeId: treeNode.id
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            settings.flashFunc("修改结点名称失败", true);
                        }
                    })
                },
                beforeRightClick: function (treeId, treeNode) {
                    zTreeObj.selectNode(treeNode);
                },
                onDrop: function (event, treeId, treeNodes, targetNode, moveType, isCopy) {
                    if (targetNode !== null && isCopy===false){
                        if (moveType === 'inner'){
                            $.ajax({
                                url: "{{ url_for('core.updateNode', type='position') }}",
                                type: 'POST',
                                data: {
                                    nodeId: treeNodes[0].id,
                                    nodePid: targetNode.id
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
        var settings = $.extend({
            nodeSeletor: '',
            dropUrl: '',
            renameUrl: '',
            addChildUrl: '',
            flashFunc: $.noop,
        }, options || {});

        $.syncNote = function(){
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
                            nodeId: node.id
                        },
                        success = function (response) {
                            zTreeObj.removeNode(node);
                        }
                    )

                } else if (key === 'addChild') {
                    newNodes = zTreeObj.addNodes(node, -1, {name: "新建节点"});
                    newNode = zTreeObj.getNodeByTId(newNodes[0].tId);
                    $.post(
                        url = settings.addChildUrl,
                        data = {
                            nodeTitle: "新建节点",
                            nodePid: node.id
                        },
                        success = function (response) {
                            newNode.id = response.nodeId;
                            zTreeObj.updateNode(newNode)
                        },
                        dataType = 'json'
                    )

                } else if (key === 'rename') {
                    zTreeObj.editName(node);

                } else if (key === 'sync') {
                    $.syncNote();
                }
            },
            items: {
                "addChild": {name: "添加子节点", icon: function () {
                        return ' icon-plus-sign-alt context-menu-awesome'
                    }},
                "sep1": "---------",
                "rename": {name: "重命名", icon: function () {
                        return 'icon-edit context-menu-awesome';
                    }},
                "drop": {name: "删除", icon: function () {
                        return 'icon-trash context-menu-awesome'
                    }},
                "sync": {name: "同步", icon: function(){
                    return 'icon-refresh context-menu-awesome';
                }}
            }
        });
    };

    $.fn.enhance = function (options) {
        var settings = $.extend({
            postUrl: '',
            previewFunc: $.noop,
            fashFunc: $.noop
        }, options || {});

        this.bind('keydown', function () {
            if (event.keyCode === 9) {
                var selectionStart = this.selectionStart;
                this.value = this.value.substring(0, selectionStart) + "    " + this.value.substring(this.selectionEnd);
                this.selectionEnd = selectionStart + 4;
                event.preventDefault();
            }
        }).bind('keyup', function () {
            content = this.value;
            if (content !== undefined) {
                settings.previewFunc(content);
                node = $.zTreeObj.getSelectedNodes()[0];
                $.ajax({
                    url: settings.postUrl,
                    type: "post",
                    data: {
                        nodeId: node.id,
                        content: content,
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        settings.flashFunc("保存失败", true);
                    }
                })


            }
        });


    }

})(jQuery);