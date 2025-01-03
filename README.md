![header](https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=10&height=200&text=School%20Service&fontSize=50&animation=twinkling&fontAlign=68&fontAlignY=36)
# 🏫 School Service  
온프레미스와 클라우드를 아우르는 통합 학교 관리 플랫폼

---

## 📅 프로젝트 기간
**2024.11.08 – 2024.12.27**

---

## 👨‍💼 팀 구성
**팀원 수:** 6명

---

## 🔠 프로젝트 개요

### 배경
기존 학교 시스템은 수강신청과 같은 고트래픽 이벤트 시, 온프레미스 리소스의 한계로 인해 성능 저하 문제가 발생했습니다.

### 목표
- 고트래픽 상황에서도 안정적인 서비스 제공
- 온프레미스와 클라우드 자원을 효율적으로 연계

### 주요 구현
- 온프레미스 우선 리소스 활용
- 리소스 초과 시 AWS로 자동 확장되는 하이브리드 구조 설계 및 구현

### 성과
- 트래픽 집중 상황에서도 안정적인 성능 보장
- 자원 활용의 유연성과 확장성 확보

---

## 📊 프로젝트 아키텍처

시스템은 온프레미스와 클라우드 환경을 결합하여 효율적으로 리소스를 관리합니다. 아래 아키텍처는 주요 구성 요소 간의 관계를 설명합니다:
![image](https://github.com/user-attachments/assets/f3176884-62c1-4e69-8861-402f6e42ce48)

### 👀 주요 특징
### 온프레미스 구성 
   - 주요 노드(Node 1 & Node 2), 예비 노드(Node 3), 그리고 전용 모니터링 및 argoCD 전용 노드
   - Nginx를 활용해 온프레미스 네트워크를 로드 밸런싱
   - Prometheus와 Grafana를 사용하여 리소스 사용량 모니터링
   
### AWS 통합
   - EKS 클러스터는 온프레미스 노드가 80% 이상의 리소스를 사용할 경우 오버플로우 트래픽을 처리
   - AWS RDS는 전용 VPN을 통해 온프레미스 데이터베이스와 안전하게 동기화

### CI/CD 파이프라인
   - GitHub Actions를 통해 지속적 통합, Docker 이미지 생성해 GHCR에 푸시
   - GitOps인 ArgoCD를 사용해 Kubernetes 매니페스트 배포를 자동화

### 모니터링 및 자동 확장
   - Prometheus는 시스템 성능을 추적하고, 확장 로직은 임계값에 도달하면 추가 리소스를 활성화

### 보안
   - VPN을 통해 온프레미스 네트워크와 AWS 간의 안전한 통신 보장

---

## ⚙️ CI/CD 파이프라인 <img src="https://img.shields.io/badge/githubactions-2088FF?style=flat-square&logo=githubactions&logoColor=white"/><img src="https://img.shields.io/badge/argo-EF7B4D?style=flat-square&logo=argo&logoColor=white"/>

빠르고 안정적인 배포를 위해 CI/CD 파이프라인을 구축했습니다. 프로세스는 다음과 같습니다:
![image](https://github.com/user-attachments/assets/9fe36166-11ab-4cd9-ba44-69a00c84f590)

### 코드 개발
   - 개발자가 GitHub 저장소에 코드를 푸시. 각 서비스 작업 후 각 서비스들의 브랜치로 푸시.
### CI 과정
  - GitHub Actions를 통한 자동 테스트.
  - Docker 이미지를 빌드하고 컨테이너 레지스트리(GHCR)에 푸시.
### CD 과정
  - Kubernetes 매니페스트를 적용하여 ArgoCD를 사용하여 애플리케이션 배포.

---

## 💃 데이터베이스 ERD <img src="https://img.shields.io/badge/mysql-4479A1?style=flat-square&logo=mysql&logoColor=white"/>

![image](https://github.com/user-attachments/assets/59765cb0-49ef-44a3-8c2d-2320d4742266)

---

## 🚀 향후 계획

### 🚧 개선 계획:
1. **CI 환경 변경:**
   - 현재 GitHub Actions를 통해 CI 환경을 구축했으나, 온프레미스 환경과 현업에서의 적용 가능성을 고려하여 Jenkins를 사용한 CI/CD 파이프라인으로의 전환을 검토 중입니다.
2. **Registry 변경:**
   - 재 GitHub Container Registry(GHCR)를 사용하여 Docker 이미지를 관리하고 있으나, 보안 강화를 위해 온프레미스에서 운영되는 Harbor로 전환할 계획입니다. 다만, 오픈소스 레지스트리의 보안 이슈와 신뢰성에 대한 추가 검토가 필요합니다.
3. **고급 인증 및 보안 강화:**
   - 기존의 AWS Cognito를 사용한 인증 방식에서, 보안 강화를 위해 우선적으로 LDAP 기반의 온프레미스 인증 시스템을 적용할 예정입니다. 이후에는 이를 확장하여 AWS Cognito를 통한 인증 연동을 고려하고 있습니다.
4. **새로운 서비스:**
   - 현 시스템에는 시간 관계상 queue 시스템이 없다. 그 뜻은 현재 만들어 놓은 서비스들은 한 과목이나 한 좌석에 트래픽이 몰렸을 때 제대로 처리를 할 수 있을지가 미지수입니다. 그래서 netFUNNEL이란 서비스를 추후에 도입할 생각이 있습니다.

## 📆 결론

이번 프로젝트는 온프레미스 인프라와 AWS 클라우드 기능을 결합하여 비용 효율적이고 확장 가능한 리소스 관리 시스템을 구현하는 데 성공했습니다. 확장성과 성능을 최적화하여 고트래픽 이벤트 발생 시에도 안정적인 서비스를 제공합니다.

이번 프로젝트를 통해 얻은 경험은 향후 더 복잡한 시스템을 구축하는데 도움이 될거라 생각하고, 스타트업이나 초기 자본이 적은 회사에서 트래픽이 몰릴 수 있는 서비스를 만들었을 때 어떻게 진행해야할지에 대한 방향성을 제시한 것이라고도 생각하게 되었습니다.
