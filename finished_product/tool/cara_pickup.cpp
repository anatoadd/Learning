#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>

class CharacterExtractor {
private:
    cv::dnn::Net net;
    std::vector<std::string> classes;
    
    void loadModel() {
        // YOLOv3モデルの読み込み
        net = cv::dnn::readNetFromDarknet("yolov3.cfg", "yolov3.weights");
        net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
        net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);
        
        // クラス名の読み込み
        std::ifstream classFile("coco.names");
        std::string line;
        while (std::getline(classFile, line)) {
            classes.push_back(line);
        }
    }

public:
    CharacterExtractor() {
        loadModel();
    }
    
    cv::Mat extractCharacter(const cv::Mat& image) {
        cv::Mat blob;
        cv::dnn::blobFromImage(image, blob, 1/255.0, cv::Size(416, 416), cv::Scalar(), true, false);
        
        net.setInput(blob);
        std::vector<cv::Mat> outs;
        net.forward(outs, net.getUnconnectedOutLayersNames());
        
        std::vector<cv::Rect> boxes;
        std::vector<float> confidences;
        std::vector<int> classIds;
        
        // 検出結果の解析
        for (const auto& out : outs) {
            for (int i = 0; i < out.rows; ++i) {
                cv::Mat scores = out.row(i).colRange(5, out.cols);
                cv::Point classIdPoint;
                double confidence;
                cv::minMaxLoc(scores, nullptr, &confidence, nullptr, &classIdPoint);
                
                if (confidence > 0.5) {  // 信頼度のしきい値
                    int centerX = (int)(out.at<float>(i, 0) * image.cols);
                    int centerY = (int)(out.at<float>(i, 1) * image.rows);
                    int width = (int)(out.at<float>(i, 2) * image.cols);
                    int height = (int)(out.at<float>(i, 3) * image.rows);
                    
                    cv::Rect box(centerX - width/2, centerY - height/2, width, height);
                    boxes.push_back(box);
                    confidences.push_back((float)confidence);
                    classIds.push_back(classIdPoint.x);
                }
            }
        }
        
        // Non-maximum suppression
        std::vector<int> indices;
        cv::dnn::NMSBoxes(boxes, confidences, 0.5, 0.4, indices);
        
        // マスク画像の作成
        cv::Mat mask = cv::Mat::zeros(image.size(), CV_8UC1);
        for (size_t i = 0; i < indices.size(); ++i) {
            cv::rectangle(mask, boxes[indices[i]], cv::Scalar(255), -1);
        }
        
        // 元画像から対象領域を切り出し
        cv::Mat result;
        image.copyTo(result, mask);
        
        return result;
    }
};

int main() {
    try {
        CharacterExtractor extractor;
        
        // 画像の読み込み
        cv::Mat image = cv::imread("input.jpg");
        if (image.empty()) {
            throw std::runtime_error("画像を読み込めませんでした。");
        }
        
        // キャラクター抽出
        cv::Mat result = extractor.extractCharacter(image);
        
        // 結果の保存
        cv::imwrite("output.jpg", result);
        std::cout << "処理が完了しました。" << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "エラーが発生しました: " << e.what() << std::endl;
        return -1;
    }
    
    return 0;
}
