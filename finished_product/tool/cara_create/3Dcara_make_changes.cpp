#include <opencv2/opencv.hpp>
#include <vector>
#include <string>
#include <stdexcept>
#include <fstream>
#include <map>
#include <unordered_map>
#include <GLFW/glfw3.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <chrono>
#include <thread>
#include <GL/gl.h>
#include <cmath>

// アニメーション用のキーフレーム構造体
struct KeyFrame {
    float time;
    cv::Point3f position;
    cv::Point3f rotation;
    cv::Point3f scale;
};

// パーツ情報を管理する構造体 
struct PartData {
    std::vector<cv::Point3f> vertices;
    std::vector<std::vector<int>> faces;
    std::vector<cv::Vec3f> normals;
    bool isVisible = true;
    ImVec4 color = ImVec4(1.0f, 1.0f, 1.0f, 1.0f);
    // パーツの寸法パラメータ
    float length = 1.0f;  // 長さ
    float width = 1.0f;   // 幅
    float thickness = 1.0f; // 太さ
    // 元の寸法を保存
    std::vector<cv::Point3f> originalVertices;
    // アニメーション用のキーフレーム
    std::vector<KeyFrame> keyFrames;
    bool isAnimating = false;
    // 回転用パラメータ
    float rotationX = 0.0f;
    float rotationY = 0.0f;
    float rotationZ = 0.0f;
    // 肌の設定
    bool isSkin = false;  // 肌パーツかどうか
    bool isTanned = false; // 日焼けしているかどうか
    ImVec4 originalSkinColor = ImVec4(1.0f, 0.8f, 0.6f, 1.0f); // 元の肌色
    ImVec4 tannedColor = ImVec4(0.8f, 0.6f, 0.4f, 1.0f); // 日焼けした肌色
    bool isClothing = false; // 服装パーツかどうか
    bool isTanLine = false;  // 日焼け跡として使用するかどうか
    // 装飾品の設定
    std::string category = ""; // パーツのカテゴリ(服、装飾品など)
    bool isAccessory = false; // 装飾品かどうか
    std::vector<std::string> compatibleParts; // 組み合わせ可能なパーツ名
    // 服装の重なり設定
    float layerDepth = 0.0f; // 服の重なり順(値が大きいほど外側)
    bool hasGap = false; // 隙間があるかどうか(鎧の関節など)
    std::vector<cv::Point3f> gapVertices; // 隙間の頂点情報
    bool isUndergarment = false; // 下着かどうか
};

class Character3DEditor {
private:
    std::unordered_map<std::string, PartData> parts;
    GLFWwindow* window;
    std::string selectedPart;
    int selectedVertex = -1;
    float editScale = 1.0f;
    bool showGrid = true;
    bool showWireframe = false;
    
    // カテゴリ管理
    std::vector<std::string> categories = {"体", "服", "装飾品"};
    std::unordered_map<std::string, std::vector<std::string>> categoryParts;
    
    // 全体の肌色設定
    ImVec4 globalSkinColor = ImVec4(1.0f, 0.8f, 0.6f, 1.0f);
    ImVec4 globalTannedColor = ImVec4(0.8f, 0.6f, 0.4f, 1.0f);
    bool globalTanningEnabled = false;
    
    // アニメーション制御用変数
    bool isPlaying = false;
    bool isPaused = false;
    float currentTime = 0.0f;
    float animationSpeed = 1.0f;
    
    // 編集用の変数
    float positionDelta[3] = {0.0f, 0.0f, 0.0f};
    float scaleDelta[3] = {1.0f, 1.0f, 1.0f};
    float rotationDelta[3] = {0.0f, 0.0f, 0.0f};
    
    // カメラ設定
    float cameraPosition[3] = {0.0f, 0.0f, 5.0f};
    float cameraRotation[3] = {0.0f, 0.0f, 0.0f}; // pitch, yaw, roll
    float cameraZoom = 1.0f;
    bool isDragging = false;
    double lastMouseX = 0.0;
    double lastMouseY = 0.0;

    // 服装の重なり処理用
    void renderClothingLayers() {
        // レイヤー順にソートされたパーツリストを作成
        std::vector<std::pair<std::string, PartData*>> sortedParts;
        for (auto& [name, part] : parts) {
            if (part.isVisible && part.isClothing) {
                sortedParts.push_back({name, &part});
            }
        }
        std::sort(sortedParts.begin(), sortedParts.end(),
            [](const auto& a, const auto& b) {
                return a.second->layerDepth < b.second->layerDepth;
            });

        // 肌パーツを最初に描画
        for (const auto& [name, part] : parts) {
            if (part.isVisible && part.isSkin) {
                renderPart(part);
            }
        }

        // 服装パーツをレイヤー順に描画
        for (const auto& [name, part] : sortedParts) {
            if (part->hasGap) {
                // 隙間のある部分は特別な処理
                renderPartWithGaps(*part);
            } else {
                renderPart(*part);
            }
        }
    }

    void renderPartWithGaps(const PartData& part) {
        glEnable(GL_STENCIL_TEST);
        glStencilFunc(GL_ALWAYS, 1, 0xFF);
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);
        
        // 通常のパーツ描画
        renderPart(part);
        
        // 隙間部分の描画
        glStencilFunc(GL_NOTEQUAL, 1, 0xFF);
        glBegin(GL_TRIANGLES);
        for (size_t i = 0; i < part.gapVertices.size(); i += 3) {
            const auto& v1 = part.gapVertices[i];
            const auto& v2 = part.gapVertices[i + 1];
            const auto& v3 = part.gapVertices[i + 2];
            glVertex3f(v1.x, v1.y, v1.z);
            glVertex3f(v2.x, v2.y, v2.z);
            glVertex3f(v3.x, v3.y, v3.z);
        }
        glEnd();
        
        glDisable(GL_STENCIL_TEST);
    }

public:
    Character3DEditor() {
        // GLFWの初期化
        if (!glfwInit()) {
            throw std::runtime_error("GLFWの初期化に失敗しました。");
        }

        // OpenGL 3.0 + GLSLを使用
        const char* glsl_version = "#version 130";
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
        glfwWindowHint(GLFW_STENCIL_BITS, 8); // ステンシルバッファを有効化

        // ウィンドウの作成
        window = glfwCreateWindow(1280, 720, "3Dキャラクター編集ツール", NULL, NULL);
        if (window == NULL) {
            glfwTerminate();
            throw std::runtime_error("ウィンドウの作成に失敗しました。");
        }

        glfwMakeContextCurrent(window);
        glfwSwapInterval(1);

        // マウスボタンのコールバック設定
        glfwSetMouseButtonCallback(window, [](GLFWwindow* w, int button, int action, int mods) {
            auto* editor = static_cast<Character3DEditor*>(glfwGetWindowUserPointer(w));
            if (button == GLFW_MOUSE_BUTTON_LEFT) {
                if (action == GLFW_PRESS) {
                    editor->isDragging = true;
                    glfwGetCursorPos(w, &editor->lastMouseX, &editor->lastMouseY);
                } else if (action == GLFW_RELEASE) {
                    editor->isDragging = false;
                }
            }
        });

        // カーソル位置のコールバック設定
        glfwSetCursorPosCallback(window, [](GLFWwindow* w, double xpos, double ypos) {
            auto* editor = static_cast<Character3DEditor*>(glfwGetWindowUserPointer(w));
            if (editor->isDragging) {
                double deltaX = xpos - editor->lastMouseX;
                double deltaY = ypos - editor->lastMouseY;
                
                editor->cameraRotation[1] += static_cast<float>(deltaX) * 0.01f;
                editor->cameraRotation[0] += static_cast<float>(deltaY) * 0.01f;
                
                editor->lastMouseX = xpos;
                editor->lastMouseY = ypos;
            }
        });

        // スクロールコールバック設定
        glfwSetScrollCallback(window, [](GLFWwindow* w, double xoffset, double yoffset) {
            auto* editor = static_cast<Character3DEditor*>(glfwGetWindowUserPointer(w));
            editor->cameraZoom += static_cast<float>(yoffset) * 0.1f;
            if (editor->cameraZoom < 0.1f) editor->cameraZoom = 0.1f;
            if (editor->cameraZoom > 10.0f) editor->cameraZoom = 10.0f;
        });

        glfwSetWindowUserPointer(window, this);

        // ImGuiの初期化
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGuiIO& io = ImGui::GetIO();
        io.ConfigFlags |= ImGuiConfigFlags_DockingEnable;
        io.ConfigFlags |= ImGuiConfigFlags_ViewportsEnable;
        
        ImGui::StyleColorsDark();
        ImGui_ImplGlfw_InitForOpenGL(window, true);
        ImGui_ImplOpenGL3_Init(glsl_version);

        // OpenGL初期設定
        glEnable(GL_DEPTH_TEST);
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glEnable(GL_STENCIL_TEST);
    }

    ~Character3DEditor() {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();
        glfwDestroyWindow(window);
        glfwTerminate();
    }

    // キーフレームの追加
    void addKeyFrame(const std::string& partName, float time) {
        auto& part = parts[partName];
        KeyFrame keyFrame;
        keyFrame.time = time;
        keyFrame.position = cv::Point3f(positionDelta[0], positionDelta[1], positionDelta[2]);
        keyFrame.rotation = cv::Point3f(rotationDelta[0], rotationDelta[1], rotationDelta[2]);
        keyFrame.scale = cv::Point3f(scaleDelta[0], scaleDelta[1], scaleDelta[2]);
        part.keyFrames.push_back(keyFrame);
    }

    // アニメーションの更新
    void updateAnimation() {
        if (!isPlaying || isPaused) return;
        
        currentTime += ImGui::GetIO().DeltaTime * animationSpeed;
        
        for (auto& [partName, part] : parts) {
            if (!part.isAnimating || part.keyFrames.empty()) continue;
            
            // キーフレーム間の補間
            for (size_t i = 0; i < part.keyFrames.size() - 1; i++) {
                if (currentTime >= part.keyFrames[i].time && 
                    currentTime < part.keyFrames[i + 1].time) {
                    float t = (currentTime - part.keyFrames[i].time) / 
                             (part.keyFrames[i + 1].time - part.keyFrames[i].time);
                    
                    // 線形補間
                    auto& k1 = part.keyFrames[i];
                    auto& k2 = part.keyFrames[i + 1];
                    
                    for (int j = 0; j < 3; j++) {
                        positionDelta[j] = k1.position.x * (1-t) + k2.position.x * t;
                        rotationDelta[j] = k1.rotation.x * (1-t) + k2.rotation.x * t;
                        scaleDelta[j] = k1.scale.x * (1-t) + k2.scale.x * t;
                    }
                    
                    applyTransformation(partName);
                    break;
                }
            }
        }
    }

    void loadModel(const std::string& filename) {
        // 既存のloadModel実装...
    }

    void saveModel(const std::string& filename) {
        // 既存のsaveModel実装...
    }

    void renderUI() {
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();
            updateAnimation();

            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // 3Dビューの設定
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT);
            glLoadIdentity();
            
            // カメラの位置設定
            glTranslatef(0.0f, 0.0f, -5.0f * cameraZoom);
            glRotatef(cameraRotation[0] * 180.0f / 3.14159f, 1.0f, 0.0f, 0.0f);
            glRotatef(cameraRotation[1] * 180.0f / 3.14159f, 0.0f, 1.0f, 0.0f);
            glRotatef(cameraRotation[2] * 180.0f / 3.14159f, 0.0f, 0.0f, 1.0f);

            // メインメニューバー
            if (ImGui::BeginMainMenuBar()) {
                if (ImGui::BeginMenu("表示")) {
                    ImGui::Checkbox("グリッド表示", &showGrid);
                    ImGui::Checkbox("ワイヤーフレーム表示", &showWireframe);
                    ImGui::EndMenu();
                }
                
                if (ImGui::BeginMenu("アニメーション")) {
                    if (ImGui::MenuItem(isPlaying ? "停止" : "再生")) {
                        isPlaying = !isPlaying;
                        isPaused = false;
                    }
                    if (ImGui::MenuItem("一時停止")) {
                        isPaused = !isPaused;
                    }
                    if (ImGui::MenuItem("リセット")) {
                        currentTime = 0.0f;
                        isPlaying = false;
                        isPaused = false;
                    }
                    ImGui::SliderFloat("再生速度", &animationSpeed, 0.1f, 2.0f);
                    ImGui::EndMenu();
                }

                if (ImGui::BeginMenu("肌色設定")) {
                    ImGui::ColorEdit4("基本肌色", &globalSkinColor.x);
                    ImGui::ColorEdit4("日焼け肌色", &globalTannedColor.x);
                    if (ImGui::Checkbox("全体日焼けモード", &globalTanningEnabled)) {
                        // 全体の日焼けモード切り替え時の処理
                        for (auto& [name, part] : parts) {
                            if (part.isSkin) {
                                part.isTanned = globalTanningEnabled;
                                part.color = globalTanningEnabled ? globalTannedColor : globalSkinColor;
                            }
                        }
                    }
                    ImGui::EndMenu();
                }
                ImGui::EndMainMenuBar();
            }

            // パーツパネル
            ImGui::Begin("パーツ一覧");
            
            // カテゴリごとにパーツを表示
            for (const auto& category : categories) {
                if (ImGui::TreeNode(category.c_str())) {
                    for (auto& [partName, partData] : parts) {
                        if (partData.category == category) {
                            if (ImGui::TreeNode(partName.c_str())) {
                                ImGui::Checkbox("表示", &partData.isVisible);
                                
                                // 肌パーツの設定
                                if (ImGui::Checkbox("肌パーツとして設定", &partData.isSkin)) {
                                    if (partData.isSkin) {
                                        partData.color = globalSkinColor;
                                        partData.originalSkinColor = globalSkinColor;
                                    }
                                }

                                // 服装パーツの設定
                                if (ImGui::Checkbox("服装パーツとして設定", &partData.isClothing)) {
                                    if (partData.isClothing) {
                                        ImGui::Checkbox("日焼け跡として使用", &partData.isTanLine);
                                        ImGui::Checkbox("下着として設定", &partData.isUndergarment);
                                        ImGui::SliderFloat("レイヤー深度", &partData.layerDepth, 0.0f, 10.0f);
                                        ImGui::Checkbox("隙間あり", &partData.hasGap);
                                    }
                                }

                                // 装飾品の設定
                                if (ImGui::Checkbox("装飾品として設定", &partData.isAccessory)) {
                                    if (partData.isAccessory) {
                                        // 装飾品の組み合わせ設定
                                        for (auto& [otherName, otherPart] : parts) {
                                            if (otherName != partName) {
                                                bool isCompatible = std::find(partData.compatibleParts.begin(), 
                                                                           partData.compatibleParts.end(), 
                                                                           otherName) != partData.compatibleParts.end();
                                                if (ImGui::Checkbox(("組み合わせ可能: " + otherName).c_str(), &isCompatible)) {
                                                    if (isCompatible) {
                                                        partData.compatibleParts.push_back(otherName);
                                                    } else {
                                                        auto it = std::find(partData.compatibleParts.begin(), 
                                                                          partData.compatibleParts.end(), 
                                                                          otherName);
                                                        if (it != partData.compatibleParts.end()) {
                                                            partData.compatibleParts.erase(it);
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }

                                // 肌パーツの場合の追加設定
                                if (partData.isSkin) {
                                    if (ImGui::Checkbox("日焼け", &partData.isTanned)) {
                                        partData.color = partData.isTanned ? globalTannedColor : globalSkinColor;
                                    }
                                }

                                if (!partData.isSkin) {
                                    ImGui::ColorEdit4("色", &partData.color.x);
                                }
                                
                                // 回転コントロール
                                ImGui::SliderFloat("X軸回転", &partData.rotationX, -180.0f, 180.0f);
                                ImGui::SliderFloat("Y軸回転", &partData.rotationY, -180.0f, 180.0f);
                                ImGui::SliderFloat("Z軸回転", &partData.rotationZ, -180.0f, 180.0f);
                                
                                ImGui::Checkbox("アニメーション有効", &partData.isAnimating);
                                if (partData.isAnimating) {
                                    if (ImGui::Button("キーフレーム追加")) {
                                        addKeyFrame(partName, currentTime);
                                    }
                                }
                                ImGui::TreePop();
                            }
                        }
                    }
                    ImGui::TreePop();
                }
            }
            ImGui::End();

            // 3Dモデルの描画
            if (showGrid) {
                drawGrid();
            }
            
            // レイヤー順に描画
            renderClothingLayers();

            ImGui::Render();
            int display_w, display_h;
            glfwGetFramebufferSize(window, &display_w, &display_h);
            glViewport(0, 0, display_w, display_h);
            
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

            if (ImGui::GetIO().ConfigFlags & ImGuiConfigFlags_ViewportsEnable) {
                GLFWwindow* backup_current_context = glfwGetCurrentContext();
                ImGui::UpdatePlatformWindows();
                ImGui::RenderPlatformWindowsDefault();
                glfwMakeContextCurrent(backup_current_context);
            }

            glfwSwapBuffers(window);
        }
    }

private:
    void renderPart(const PartData& part) {
        glPushMatrix();
        
        // パーツの回転を適用
        glRotatef(part.rotationX, 1.0f, 0.0f, 0.0f);
        glRotatef(part.rotationY, 0.0f, 1.0f, 0.0f);
        glRotatef(part.rotationZ, 0.0f, 0.0f, 1.0f);

        // ワイヤーフレームモード設定
        if (showWireframe) {
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
        } else {
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
        }

        // 日焼け跡の処理
        if (part.isClothing && part.isTanLine) {
            glColor4f(globalTannedColor.x, globalTannedColor.y, globalTannedColor.z, globalTannedColor.w);
        } else {
            glColor4f(part.color.x, part.color.y, part.color.z, part.color.w);
        }

        glBegin(GL_TRIANGLES);
        for (const auto& face : part.faces) {
            for (int vertexIndex : face) {
                const auto& vertex = part.vertices[vertexIndex];
                if (part.normals.size() > vertexIndex) {
                    const auto& normal = part.normals[vertexIndex];
                    glNormal3f(normal[0], normal[1], normal[2]);
                }
                glVertex3f(vertex.x, vertex.y, vertex.z);
            }
        }
        glEnd();

        glPopMatrix();
    }

    void drawGrid() {
        glColor3f(0.5f, 0.5f, 0.5f);
        glBegin(GL_LINES);
        for (float i = -10.0f; i <= 10.0f; i += 1.0f) {
            glVertex3f(i, 0, -10.0f);
            glVertex3f(i, 0, 10.0f);
            glVertex3f(-10.0f, 0, i);
            glVertex3f(10.0f, 0, i);
        }
        glEnd();
    }
};

int main() {
    try {
        Character3DEditor editor;
        editor.renderUI();
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "エラーが発生しました: " << e.what() << std::endl;
        return -1;
    }
}
