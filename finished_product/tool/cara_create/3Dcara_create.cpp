#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
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
#include <filesystem>

// パーツ情報を管理する構造体
struct PartData {
    std::vector<cv::Point3f> vertices;
    std::vector<std::vector<int>> faces;
    std::vector<cv::Vec3f> normals;
    int sampleCount; // このパーツのデータ数
    float confidence; // 信頼度(データ数に基づく)
    
    // パーツのサイズ情報
    float width;  // 幅
    float height; // 高さ 
    float depth;  // 奥行き
    float volume; // 体積
    float surfaceArea; // 表面積
    
    // 位置情報
    cv::Point3f centerPoint; // 中心座標
    cv::Point3f minBounds;   // 最小境界座標
    cv::Point3f maxBounds;   // 最大境界座標
    
    // パーツの種類
    bool isClothing; // 服装パーツかどうか

    // 推測データの管理
    std::vector<bool> isEstimated; // 各頂点が推測されたものかどうか
    float estimatedRatio; // 推測された部分の割合
    std::string estimationNotes; // 推測に関する注意事項
};

class Character3DCreator {
private:
    std::unordered_map<std::string, PartData> parts; // パーツごとのデータ
    std::vector<cv::Mat> depthMaps;
    std::vector<cv::Mat> normalMaps;
    cv::Mat finalDepthMap;
    cv::Mat finalNormalMap;
    bool hasExistingData;
    GLFWwindow* window;

    // パーツの定義
    const std::vector<std::string> characterParts = {
        "head", "body", "right_arm", "left_arm", 
        "right_hand", "left_hand", "right_leg", "left_leg",
        "right_foot", "left_foot"
    };

    const std::vector<std::string> clothingParts = {
        "hat", "shirt", "pants", "shoes", "accessories"
    };

    // データ保存用のパス
    const std::string characterDataPath = "3Dcara_data/";
    const std::string clothingDataPath = "Clothing_Decoration_data/";

public:
    Character3DCreator() : hasExistingData(false) {
        // データ保存用ディレクトリの作成
        std::filesystem::create_directories(characterDataPath);
        std::filesystem::create_directories(clothingDataPath);

        // GLFWの初期化
        if (!glfwInit()) {
            throw std::runtime_error("GLFWの初期化に失敗しました。");
        }

        // OpenGL 3.0 + GLSLを使用
        const char* glsl_version = "#version 130";
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

        // ウィンドウの作成
        window = glfwCreateWindow(1280, 720, "3Dキャラクタークリエーター", NULL, NULL);
        if (window == NULL) {
            glfwTerminate();
            throw std::runtime_error("ウィンドウの作成に失敗しました。");
        }

        glfwMakeContextCurrent(window);
        glfwSwapInterval(1); // VSyncを有効化

        // ImGuiの初期化
        IMGUI_CHECKVERSION();
        ImGui::CreateContext();
        ImGui::StyleColorsDark();
        ImGui_ImplGlfw_InitForOpenGL(window, true);
        ImGui_ImplOpenGL3_Init(glsl_version);

        // キャラクターパーツの初期化
        for(const auto& partName : characterParts) {
            parts[partName] = PartData();
            initializePartData(parts[partName], false);
        }

        // 服装パーツの初期化
        for(const auto& partName : clothingParts) {
            parts[partName] = PartData();
            initializePartData(parts[partName], true);
        }
    }

    ~Character3DCreator() {
        ImGui_ImplOpenGL3_Shutdown();
        ImGui_ImplGlfw_Shutdown();
        ImGui::DestroyContext();
        glfwDestroyWindow(window);
        glfwTerminate();
    }

    void renderUI() {
        while (!glfwWindowShouldClose(window)) {
            glfwPollEvents();

            ImGui_ImplOpenGL3_NewFrame();
            ImGui_ImplGlfw_NewFrame();
            ImGui::NewFrame();

            // メインウィンドウ
            ImGui::Begin("3Dキャラクタークリエーター");

            if (ImGui::Button("モデルを読み込む")) {
                try {
                    loadExistingModel("previous_model.obj");
                } catch (const std::exception& e) {
                    ImGui::OpenPopup("エラー");
                }
            }

            if (ImGui::Button("キャラクターを保存")) {
                try {
                    exportToObj(characterDataPath + "character.obj", false);
                } catch (const std::exception& e) {
                    ImGui::OpenPopup("エラー");
                }
            }

            if (ImGui::Button("服装を保存")) {
                try {
                    exportToObj(clothingDataPath + "clothing.obj", true);
                } catch (const std::exception& e) {
                    ImGui::OpenPopup("エラー");
                }
            }

            // パーツ情報の表示
            ImGui::Text("キャラクターパーツ:");
            for (const auto& partName : characterParts) {
                const auto& partData = parts[partName];
                ImGui::Text("%s: サイズ(W:%.2f H:%.2f D:%.2f) 体積:%.2f 表面積:%.2f", 
                    partName.c_str(), 
                    partData.width, partData.height, partData.depth,
                    partData.volume, partData.surfaceArea);
                
                // 推測データの表示
                if (partData.estimatedRatio > 0.0f) {
                    ImGui::TextColored(ImVec4(1.0f, 0.8f, 0.0f, 1.0f), 
                        "注意: このパーツの%.1f%%が推測データです", 
                        partData.estimatedRatio * 100.0f);
                    ImGui::TextWrapped("%s", partData.estimationNotes.c_str());
                }
            }

            ImGui::Text("\n服装パーツ:");
            for (const auto& partName : clothingParts) {
                const auto& partData = parts[partName];
                ImGui::Text("%s: サイズ(W:%.2f H:%.2f D:%.2f) 体積:%.2f 表面積:%.2f", 
                    partName.c_str(), 
                    partData.width, partData.height, partData.depth,
                    partData.volume, partData.surfaceArea);
                
                // 推測データの表示
                if (partData.estimatedRatio > 0.0f) {
                    ImGui::TextColored(ImVec4(1.0f, 0.8f, 0.0f, 1.0f), 
                        "注意: このパーツの%.1f%%が推測データです", 
                        partData.estimatedRatio * 100.0f);
                    ImGui::TextWrapped("%s", partData.estimationNotes.c_str());
                }
            }

            ImGui::End();

            // エラーポップアップ
            if (ImGui::BeginPopupModal("エラー", NULL, ImGuiWindowFlags_AlwaysAutoResize)) {
                ImGui::Text("処理中にエラーが発生しました。");
                if (ImGui::Button("OK")) {
                    ImGui::CloseCurrentPopup();
                }
                ImGui::EndPopup();
            }

            ImGui::Render();
            int display_w, display_h;
            glfwGetFramebufferSize(window, &display_w, &display_h);
            glViewport(0, 0, display_w, display_h);
            glClearColor(0.45f, 0.55f, 0.60f, 1.00f);
            glClear(GL_COLOR_BUFFER_BIT);
            ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

            glfwSwapBuffers(window);
        }
    }

    void loadExistingModel(const std::string& objFile) {
        std::ifstream in(objFile);
        if(!in.is_open()) {
            throw std::runtime_error("既存モデルを読み込めませんでした。");
        }

        std::string currentPart;
        std::string line;
        
        while(std::getline(in, line)) {
            if(line.substr(0,2) == "# ") {
                // パーツ情報の読み込み
                std::string info = line.substr(2);
                size_t pos = info.find(":");
                if(pos != std::string::npos) {
                    currentPart = info.substr(0, pos);
                    sscanf(info.substr(pos+1).c_str(), "%d %f %f %f %f %f %f", 
                           &parts[currentPart].sampleCount,
                           &parts[currentPart].width,
                           &parts[currentPart].height,
                           &parts[currentPart].depth,
                           &parts[currentPart].volume,
                           &parts[currentPart].surfaceArea,
                           &parts[currentPart].confidence);
                }
            }
            else if(line[0] == 'v' && line[1] == ' ') {
                float x, y, z;
                sscanf(line.c_str(), "v %f %f %f", &x, &y, &z);
                if(!currentPart.empty()) {
                    parts[currentPart].vertices.push_back(cv::Point3f(x, y, z));
                    parts[currentPart].isEstimated.push_back(false); // デフォルトでは推測データではない
                    updatePartBounds(parts[currentPart], cv::Point3f(x, y, z));
                }
            }
            else if(line[0] == 'v' && line[1] == 'n') {
                float nx, ny, nz;
                sscanf(line.c_str(), "vn %f %f %f", &nx, &ny, &nz);
                if(!currentPart.empty()) {
                    parts[currentPart].normals.push_back(cv::Vec3f(nx, ny, nz));
                }
            }
            else if(line[0] == 'f') {
                std::vector<int> face;
                std::stringstream ss(line.substr(2));
                std::string vertex;
                while(ss >> vertex) {
                    face.push_back(std::stoi(vertex.substr(0, vertex.find("//"))) - 1);
                }
                if(!currentPart.empty()) {
                    parts[currentPart].faces.push_back(face);
                }
            }
        }
        
        hasExistingData = true;
        in.close();
        
        // 各パーツのサイズ情報を更新
        for(auto& [partName, partData] : parts) {
            calculatePartDimensions(partData);
            updateEstimationInfo(partData); // 推測データの情報を更新
        }
    }

    void exportToObj(const std::string& filename, bool clothingOnly) {
        std::ofstream out(filename);
        if(!out.is_open()) {
            throw std::runtime_error("ファイルを開けませんでした。");
        }

        int vertexOffset = 0;
        
        for(const auto& [partName, partData] : parts) {
            // 服装パーツのみまたはキャラクターパーツのみを出力
            if(partData.isClothing != clothingOnly) continue;

            // パーツ情報のヘッダー出力
            out << "# " << partName << ": " 
                << partData.sampleCount << " "
                << partData.width << " "
                << partData.height << " "
                << partData.depth << " "
                << partData.volume << " "
                << partData.surfaceArea << " "
                << partData.confidence << "\n";

            // 推測データに関する注意事項を出力
            if (partData.estimatedRatio > 0.0f) {
                out << "# ESTIMATION_NOTE: " << partData.estimationNotes << "\n";
            }

            // 頂点と法線の出力
            for(size_t i = 0; i < partData.vertices.size(); i++) {
                const auto& v = partData.vertices[i];
                const auto& n = partData.normals[i];
                out << "v " << v.x << " " << v.y << " " << v.z << "\n";
                out << "vn " << n[0] << " " << n[1] << " " << n[2] << "\n";
            }

            // 面の出力
            for(const auto& f : partData.faces) {
                out << "f";
                for(int idx : f) {
                    out << " " << (idx + vertexOffset + 1) << "//" << (idx + vertexOffset + 1);
                }
                out << "\n";
            }

            vertexOffset += partData.vertices.size();
        }

        out.close();
    }

    float calculateWeight(const std::string& partName) {
        const auto& part = parts[partName];
        if(part.sampleCount == 0) return 1.0f;
        return 1.0f / (1.0f + std::log(part.sampleCount + 1));
    }
    
private:
    void initializePartData(PartData& part, bool isClothing) {
        part.sampleCount = 0;
        part.confidence = 0.0f;
        part.width = 0.0f;
        part.height = 0.0f;
        part.depth = 0.0f;
        part.volume = 0.0f;
        part.surfaceArea = 0.0f;
        part.centerPoint = cv::Point3f(0.0f, 0.0f, 0.0f);
        part.minBounds = cv::Point3f(0.0f, 0.0f, 0.0f);
        part.maxBounds = cv::Point3f(0.0f, 0.0f, 0.0f);
        part.isClothing = isClothing;
        part.estimatedRatio = 0.0f;
        part.estimationNotes = "";
    }

    void updatePartBounds(PartData& part, const cv::Point3f& vertex) {
        // 最小・最大境界を更新
        part.minBounds.x = std::min(part.minBounds.x, vertex.x);
        part.minBounds.y = std::min(part.minBounds.y, vertex.y);
        part.minBounds.z = std::min(part.minBounds.z, vertex.z);
        
        part.maxBounds.x = std::max(part.maxBounds.x, vertex.x);
        part.maxBounds.y = std::max(part.maxBounds.y, vertex.y);
        part.maxBounds.z = std::max(part.maxBounds.z, vertex.z);
        
        // 中心点を更新
        part.centerPoint = (part.minBounds + part.maxBounds) * 0.5f;
    }
    
    void calculatePartDimensions(PartData& part) {
        // サイズを計算
        part.width = part.maxBounds.x - part.minBounds.x;
        part.height = part.maxBounds.y - part.minBounds.y;
        part.depth = part.maxBounds.z - part.minBounds.z;
        
        // 概算体積を計算
        part.volume = part.width * part.height * part.depth;
        
        // 表面積を計算 (三角形の面積の合計)
        part.surfaceArea = 0.0f;
        for(const auto& face : part.faces) {
            if(face.size() >= 3) {
                cv::Point3f v1 = part.vertices[face[0]];
                cv::Point3f v2 = part.vertices[face[1]];
                cv::Point3f v3 = part.vertices[face[2]];
                
                // 三角形の面積を計算
                cv::Point3f cross = (v2 - v1).cross(v3 - v1);
                float area = cv::norm(cross) * 0.5f;
                part.surfaceArea += area;
            }
        }
    }

    void updateEstimationInfo(PartData& part) {
        // 推測された頂点の数をカウント
        int estimatedCount = 0;
        for (bool isEst : part.isEstimated) {
            if (isEst) estimatedCount++;
        }

        // 推測された割合を計算
        part.estimatedRatio = static_cast<float>(estimatedCount) / part.vertices.size();

        // 推測に関する注意事項を更新
        if (part.estimatedRatio > 0.0f) {
            std::stringstream ss;
            ss << "このパーツには画像から直接見えない推測された部分が含まれています。";
            ss << "主に背面の" << (part.estimatedRatio * 100.0f) << "%が推測データです。";
            ss << "実際の形状とは異なる可能性があります。";
            part.estimationNotes = ss.str();
        }
    }
};

int main() {
    try {
        Character3DCreator creator;
        creator.renderUI();
        return 0;
    } catch(const std::exception& e) {
        std::cerr << "エラーが発生しました: " << e.what() << std::endl;
        return -1;
    }
}
